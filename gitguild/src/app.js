/* Guild emblem app: React UMD shell rendering emblem, cards, train, selection chip. */
(function () {
  'use strict';

  var React = window.React;
  var ReactDOM = window.ReactDOM;
  if (!React || !ReactDOM) return;

  var CFG = window.GUILD || {};
  var GRID = window.GUILD_GRID || {};
  var PROJECTS = CFG.projects || {};
  var ORDER = CFG.order || Object.keys(PROJECTS);
  var NS = 'http://www.w3.org/2000/svg';
  var e = React.createElement;

  var reduced = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  function slugify(name) {
    return String(name || 'project').toLowerCase()
      .replace(/[^a-z0-9]+/g, '-').replace(/^-+|-+$/g, '').replace(/-+/g, '-') || 'project';
  }
  var slugCount = {};
  var SLUGS = {};
  ORDER.forEach(function (id) {
    var base = slugify((PROJECTS[id] || {}).name || id);
    var slug = base;
    var n = 2;
    while (slugCount[slug]) { slug = base + '-' + n; n += 1; }
    slugCount[slug] = 1;
    SLUGS[id] = slug;
  });
  function pageUrl(id) { return 'projects/' + (SLUGS[id] || id) + '.html'; }

  var byId = {};
  (GRID.nodes || []).forEach(function (n) { byId[n.id] = n; });
  var SLOTTED = ORDER.slice(0, 12);
  var OVERFLOW = ORDER.slice(12);
  var indexOf = {};
  ORDER.forEach(function (id, i) { indexOf[id] = i; });
  function pad2(n) { return String(n).padStart(2, '0'); }

  function tracesOf(id) {
    return ((GRID.adjacency || {})[id] || []).map(function (en) { return en[0]; });
  }

  /* Shared UI state across the portals. ADR-0003: ring tap selects only. */
  var store = {
    hot: null,
    selected: null,
    listeners: [],
    set: function (patch) {
      for (var k in patch) store[k] = patch[k];
      store.listeners.forEach(function (fn) { fn(); });
    },
    subscribe: function (fn) {
      store.listeners.push(fn);
      return function () {
        store.listeners = store.listeners.filter(function (f) { return f !== fn; });
      };
    }
  };
  function useStore() {
    var _ = React.useState(0)[1];
    React.useEffect(function () {
      return store.subscribe(function () { _(function (x) { return x + 1; }); });
    }, []);
    return store;
  }

  function spark(i, from, dur) {
    if (reduced) return;
    var svg = document.getElementById('emblem');
    if (!svg) return;
    var g = svg.querySelector('.layer--sparks');
    if (!g) return;
    var t = (GRID.traces || [])[i];
    if (!t) return;
    var line = svg.querySelector('.trace:not(.trace--halo)[data-i="' + i + '"]');
    var L = 0;
    try { L = line ? line.getTotalLength() : (t.l || 200); } catch (err) { L = t.l || 200; }
    if (!L) return;
    var run = 24;
    if (L < run * 1.4) run = L * 0.4;
    var s = document.createElementNS(NS, 'path');
    s.setAttribute('d', t.d);
    s.setAttribute('class', 'spark spark--' + t.c);
    s.setAttribute('stroke-dasharray', run + ' ' + L);
    g.appendChild(s);
    var far = -(L - run);
    var a = (from === 'b') ? far : 0;
    var b = (from === 'b') ? 0 : far;
    s.style.strokeDashoffset = a;
    requestAnimationFrame(function () { requestAnimationFrame(function () {
      s.style.transition = 'stroke-dashoffset ' + (dur || 620) + 'ms cubic-bezier(.35,.1,.4,1)';
      s.style.strokeDashoffset = b;
    }); });
    setTimeout(function () { if (s.parentNode) s.parentNode.removeChild(s); }, (dur || 620) + 260);
  }

  function goToProject(id) {
    var url = pageUrl(id);
    try { window.location.href = url; } catch (err) { window.location = url; }
  }

  /* ADR-0003 step 2: ring tap selects only — jump slider/spotlight, light ring.
     Never navigate on first tap; the explicit Open project action navigates. */
  function selectProject(id) {
    store.set({ selected: id });
  }

  function Emblem() {
    var s = useStore();
    var svgRef = React.useRef(null);
    var active = s.hot || s.selected;
    var lit = {};
    if (active) tracesOf(active).forEach(function (i) { lit[i] = 1; });

    React.useEffect(function () {
      var svg = document.getElementById('emblem');
      if (!svg || reduced) return;
      var lines = svg.querySelectorAll('.trace:not(.trace--halo)');
      if (!lines.length) return;
      var lens = [];
      lines.forEach(function (t) { try { lens.push(t.getTotalLength()); } catch (err) { lens.push(200); } });
      lines.forEach(function (t, i) {
        t.style.strokeDasharray = lens[i];
        t.style.strokeDashoffset = lens[i];
      });
      var nodes = svg.querySelectorAll('.node');
      nodes.forEach(function (n) { n.classList.add('is-pending'); });
      var raf = requestAnimationFrame(function () { requestAnimationFrame(function () {
        lines.forEach(function (t, i) {
          var d = Math.min(900, 250 + lens[i] * 2.4);
          t.style.transition = 'stroke-dashoffset ' + d + 'ms cubic-bezier(.25,.7,.25,1) ' + (i % 12) * 26 + 'ms';
          t.style.strokeDashoffset = 0;
        });
        setTimeout(function () {
          lines.forEach(function (t) { t.style.transition = ''; t.style.strokeDasharray = ''; t.style.strokeDashoffset = ''; });
          nodes.forEach(function (g, i) {
            setTimeout(function () { g.classList.remove('is-pending'); g.classList.add('is-in'); }, i * 55);
          });
          svg.classList.add('is-ready');
          if (!reduced) {
            setTimeout(function () {
              ((GRID.adjacency || {}).n1 || []).forEach(function (en) { spark(en[0], en[1], 900); });
            }, 620);
          }
        }, 1500);
      }); });
      return function () { cancelAnimationFrame(raf); };
    }, []);

    var view = (GRID.view || [0, 0, 476, 476]).join(' ');
    var stroke = GRID.stroke || 9.6;
    var rMid = ((GRID.rIn || 11) + (GRID.rOut || 20.5)) / 2;
    var rBand = (GRID.rOut || 20.5) - (GRID.rIn || 11);

    function onNodeClick(id, ev) {
      if (ev.metaKey || ev.ctrlKey) {
        var p = PROJECTS[id] || {};
        if (p.url) { window.open(p.url, '_blank', 'noopener'); return; }
      }
      (tracesOf(id) || []).forEach(function (ti) {
        var len = ((GRID.traces || [])[ti] || {}).l || 200;
        spark(ti, 'a', Math.max(320, Math.min(900, len * 1.1)));
      });
      selectProject(id);
    }

    return e(React.Fragment, null,
      e('g', { className: 'layer layer--halos' },
        (GRID.traces || []).map(function (t) {
          return e('path', {
            key: 'h' + t.i, d: t.d,
            className: 'trace trace--' + t.c + ' trace--halo' + (lit[t.i] ? ' is-lit' : ''),
            'stroke-width': stroke * 2.6, 'stroke-linecap': 'round', 'data-i': t.i
          });
        })
      ),
      e('g', { className: 'layer layer--traces' },
        (GRID.traces || []).map(function (t) {
          return e('path', {
            key: 't' + t.i, d: t.d,
            className: 'trace trace--' + t.c + (lit[t.i] ? ' is-lit' : ''),
            'stroke-linecap': 'round', 'stroke-linejoin': 'round', 'data-i': t.i
          });
        })
      ),
      e('g', { className: 'layer layer--sparks' }),
      e('g', { className: 'layer layer--nodes', ref: svgRef },
        SLOTTED.filter(function (id) { return byId[id]; }).map(function (id) {
          var n = byId[id];
          var p = PROJECTS[id] || {};
          var isHot = s.hot === id;
          var isSel = s.selected === id;
          var near = active && (id === active || tracesOf(active).some(function (i) {
            var tr = (GRID.traces || [])[i] || {};
            return tr.a === id || tr.b === id;
          }));
          return e('g', {
            key: id,
            className: 'node node--' + n.c + ' node--' + id + (isHot ? ' is-hot' : '') + (isSel ? ' is-selected' : '') + (near && id !== active ? ' is-near' : ''),
            'data-id': id, tabIndex: '0', role: 'button',
            'aria-label': (p.name || id) + (p.tagline ? ' — ' + p.tagline : '') + ' (project ' + (indexOf[id] + 1) + ' of ' + ORDER.length + ')',
            onMouseEnter: function () { store.set({ hot: id }); },
            onMouseLeave: function () { store.set({ hot: null }); },
            onFocus: function () { store.set({ hot: id }); },
            onBlur: function () { store.set({ hot: null }); },
            onClick: function (ev) { onNodeClick(id, ev); },
            onKeyDown: function (ev) {
              if (ev.key === 'Enter' || ev.key === ' ') { ev.preventDefault(); onNodeClick(id, ev); }
              else if (ev.key === 'ArrowRight' || ev.key === 'ArrowDown') {
                ev.preventDefault();
                var si = SLOTTED.indexOf(id);
                var nx = SLOTTED[(si + 1) % SLOTTED.length];
                var elx = document.querySelector('.node[data-id="' + nx + '"]');
                if (elx) elx.focus();
              } else if (ev.key === 'ArrowLeft' || ev.key === 'ArrowUp') {
                ev.preventDefault();
                var sj = SLOTTED.indexOf(id);
                var pv = SLOTTED[(sj - 1 + SLOTTED.length) % SLOTTED.length];
                var elp = document.querySelector('.node[data-id="' + pv + '"]');
                if (elp) elp.focus();
              } else if (ev.key === 'Escape') { store.set({ hot: null }); }
            }
          },
            e('circle', { className: 'node__halo', cx: n.x, cy: n.y, r: rMid }),
            e('circle', { className: 'node__orbit', cx: n.x, cy: n.y, r: (GRID.rOut || 20.5) + 8 }),
            e('circle', { className: 'node__ring', cx: n.x, cy: n.y, r: rMid, 'stroke-width': rBand }),
            e('circle', { className: 'node__hit', cx: n.x, cy: n.y, r: 31 })
          );
        })
      )
    );
  }

  function Tip() {
    var s = useStore();
    var id = s.hot;
    if (!id) return null;
    var n = byId[id];
    var p = PROJECTS[id] || {};
    if (!n) return null;
    var v = GRID.view || [0, 0, 476, 476];
    var px = (n.x - v[0]) / v[2] * 100;
    var py = (n.y - v[1]) / v[3] * 100;
    var below = py < 26;
    return e('div', { className: 'tip is-on' + (below ? ' tip--below' : ''), id: 'tip-inner' },
      e('span', { className: 'tip__idx' }, pad2(indexOf[id] + 1)),
      e('span', { className: 'tip__name' }, (p.name || id).toUpperCase()),
      e('span', { className: 'tip__tag' }, p.tagline || ''),
      e('span', { className: 'tip__cta' }, 'View ↓')
    );
  }

  /* ADR-0003 step 3: slider as the sole browser. One state machine
     (store.selected) drives both viewports — mobile peek carousel + counter +
     dots, desktop spotlight + dense index — plus prev/next and arrow keys.
     Ring tap jumps the slider; only the active slide is focusable. */
  function stepSelection(delta) {
    var cur = store.selected || SLOTTED[0];
    var i = (SLOTTED.indexOf(cur) + delta + SLOTTED.length) % SLOTTED.length;
    store.set({ selected: SLOTTED[i] });
  }

  function nearestSlideIdx(track) {
    var slides = track.querySelectorAll('.slide');
    if (!slides.length) return 0;
    var mid = track.scrollLeft + track.clientWidth / 2;
    var best = 0, bestD = Infinity;
    slides.forEach(function (sl, i) {
      var d = Math.abs((sl.offsetLeft + sl.offsetWidth / 2) - mid);
      if (d < bestD) { bestD = d; best = i; }
    });
    return best;
  }

  function Slider() {
    var s = useStore();
    var trackRef = React.useRef(null);
    var scrollT = React.useRef(null);
    var gestured = React.useRef(false);
    var displayId = s.selected || SLOTTED[0];
    var displayIdx = Math.max(0, SLOTTED.indexOf(displayId));
    var p0 = PROJECTS[displayId] || {};

    /* Jump the carousel to the selected slide (ring tap, dots, arrows).
       Skip when already there: a no-op programmatic scroll can still emit a
       scroll event, which would wrongly adopt the first slide on load. */
    React.useEffect(function () {
      var track = trackRef.current;
      if (!track || !track.clientWidth) return;
      if (nearestSlideIdx(track) === displayIdx) return;
      var slides = track.querySelectorAll('.slide');
      var sl = slides[displayIdx];
      if (!sl) return;
      var x = sl.offsetLeft;
      try { track.scrollTo({ left: x, behavior: reduced ? 'auto' : 'smooth' }); }
      catch (err) { track.scrollLeft = x; }
    }, [displayId]);

    /* Only the active slide stays in the tab order / a11y tree. */
    React.useEffect(function () {
      var track = trackRef.current;
      if (!track) return;
      track.querySelectorAll('.slide').forEach(function (sl, i) {
        try { sl.inert = SLOTTED[i] !== displayId; } catch (err) {}
      });
    });

    /* Swipe settles onto a slide: adopt it as the selection (debounced so a
       programmatic glide does not flicker through intermediates, and gated
       on a track gesture so layout/scroll noise on load can never select). */
    function onTrackScroll() {
      var track = trackRef.current;
      if (!track) return;
      if (scrollT.current) clearTimeout(scrollT.current);
      scrollT.current = setTimeout(function () {
        if (!gestured.current) return;
        gestured.current = false;
        var id = SLOTTED[nearestSlideIdx(track)];
        if (id && id !== store.selected) store.set({ selected: id });
      }, 140);
    }

    function markGesture() { gestured.current = true; }

    function select(id) { store.set({ selected: id }); }

    var slides = SLOTTED.map(function (id, i) {
      var p = PROJECTS[id] || {};
      var active = id === displayId;
      var chips = (p.stack || []).slice(0, 3).map(function (c, j) {
        return e('li', { key: j }, c);
      });
      return e('article', {
        key: id,
        className: 'slide' + (s.hot === id ? ' is-hot' : '') + (active ? ' is-active' : ''),
        'data-id': id,
        role: 'group',
        'aria-label': (i + 1) + ' of ' + SLOTTED.length + ': ' + (p.name || id),
        'aria-hidden': active ? undefined : 'true',
        tabIndex: active ? '0' : '-1',
        onMouseEnter: function () { store.set({ hot: id }); },
        onMouseLeave: function () { store.set({ hot: null }); },
        onFocus: function () { store.set({ hot: id }); },
        onBlur: function () { store.set({ hot: null }); },
        onClick: function (ev) {
          if (ev.target.closest && ev.target.closest('a')) return;
          select(id);
        },
        onKeyDown: function (ev) {
          if (ev.key === 'Enter' || ev.key === ' ') { ev.preventDefault(); select(id); }
        }
      },
        e('span', { className: 'slide__head', 'aria-hidden': 'true' },
          e('span', { className: 'slide__idx' }, pad2(i + 1)),
          e('span', { className: 'slide__pip' }),
          p.featured ? e('span', { className: 'slide__flag' }, 'flagship') : null
        ),
        e('span', { className: 'slide__name' }, p.name || id),
        e('span', { className: 'slide__tag' }, p.tagline || ''),
        e('span', { className: 'slide__chips' }, e('ul', { className: 'chips' }, chips)),
        e('a', { className: 'slide__open', href: pageUrl(id) }, 'Open project ', e('span', { 'aria-hidden': 'true' }, '→'))
      );
    });

    var spotChips = (p0.stack || []).map(function (c, i) {
      return e('li', { key: i }, c);
    });
    var spot = e('div', { className: 'spot', id: 'spotlight', 'aria-live': 'polite' },
      e('p', { className: 'spot__idx' },
        'Node ' + pad2(displayIdx + 1) + ' / ' + pad2(SLOTTED.length),
        p0.featured ? e('span', { className: 'spot__flag' }, 'flagship') : null),
      e('h3', { className: 'spot__name' }, p0.name || displayId),
      e('p', { className: 'spot__tag' }, p0.tagline || ''),
      e('p', { className: 'spot__blurb' }, p0.blurb || ''),
      e('ul', { className: 'chips spot__chips' }, spotChips),
      e('a', { className: 'btn btn--primary spot__open', href: pageUrl(displayId) },
        'Open project ', e('span', { 'aria-hidden': 'true' }, '→'))
    );

    var index = e('ul', { className: 'sidx', 'aria-label': 'All projects' },
      SLOTTED.map(function (id, i) {
        var p = PROJECTS[id] || {};
        var active = id === displayId;
        return e('li', { key: id },
          e('button', {
            type: 'button',
            className: 'sidx__row' + (s.hot === id ? ' is-hot' : '') + (active ? ' is-active' : ''),
            'data-id': id,
            'aria-label': 'Show ' + (p.name || id) + ', ' + (i + 1) + ' of ' + SLOTTED.length + (active ? ' (current)' : ''),
            'aria-current': active ? 'true' : undefined,
            onMouseEnter: function () { if (byId[id]) store.set({ hot: id }); },
            onMouseLeave: function () { store.set({ hot: null }); },
            onFocus: function () { if (byId[id]) store.set({ hot: id }); },
            onBlur: function () { store.set({ hot: null }); },
            onClick: function () { select(id); }
          },
            e('span', { className: 'sidx__idx', 'aria-hidden': 'true' }, pad2(i + 1)),
            e('span', { className: 'sidx__name', 'aria-hidden': 'true' }, p.name || id),
            p.featured ? e('span', { className: 'sidx__flag', 'aria-hidden': 'true' }, 'flagship') : null
          ));
      }));

    var dots = e('div', { className: 'dots', role: 'group', 'aria-label': 'Choose project' },
      SLOTTED.map(function (id, i) {
        var p = PROJECTS[id] || {};
        return e('button', {
          key: id, type: 'button',
          className: 'dot' + (id === displayId ? ' is-active' : ''),
          'data-id': id,
          'aria-label': 'Show ' + (p.name || id) + ', ' + (i + 1) + ' of ' + SLOTTED.length,
          onClick: function () { select(id); }
        });
      }));

    var nav = e('div', { className: 'slider__nav' },
      e('button', {
        type: 'button', className: 'slider__step',
        'aria-label': 'Previous project',
        onClick: function () { stepSelection(-1); }
      }, e('span', { 'aria-hidden': 'true' }, '← '), 'Prev'),
      e('p', { className: 'slider__count' }, pad2(displayIdx + 1) + ' / ' + pad2(SLOTTED.length)),
      e('button', {
        type: 'button', className: 'slider__step',
        'aria-label': 'Next project',
        onClick: function () { stepSelection(1); }
      }, 'Next', e('span', { 'aria-hidden': 'true' }, ' →')));

    /* ADR-0002 overflow: beyond 12 slots, card-only rows with no ring. */
    var overflow = OVERFLOW.length ? e('ul', { className: 'overflow', 'aria-label': 'More projects' },
      OVERFLOW.map(function (id) {
        var p = PROJECTS[id] || {};
        return e('li', { key: id },
          e('a', { className: 'overflow__row', href: pageUrl(id) },
            e('span', { className: 'overflow__name' }, p.name || id),
            e('span', { className: 'overflow__flag' }, 'card only')));
      })) : null;

    return e('div', {
      className: 'slider',
      role: 'region', 'aria-roledescription': 'carousel', 'aria-label': 'Projects',
      onKeyDown: function (ev) {
        if (ev.key === 'ArrowRight') { ev.preventDefault(); stepSelection(1); }
        else if (ev.key === 'ArrowLeft') { ev.preventDefault(); stepSelection(-1); }
      }
    }, spot,
      e('div', { className: 'carousel' },
        e('div', {
          className: 'carousel__track', ref: trackRef, onScroll: onTrackScroll,
          onPointerDown: markGesture, onWheel: markGesture, onTouchStart: markGesture
        }, slides)),
      index, nav, dots, overflow
    );
  }

  function Train() {
    var s = useStore();
    var TRAIN = CFG.mergeTrain || ['n11', 'n9', 'n6', 'n1', 'n5', 'n0'];
    var y = 96, x0 = 190, step = 164;
    function go(id) { goToProject(id); }
    return e('g', null,
      e('path', { className: 'train__trunk', d: 'M64,' + y + 'H1144' }),
      e('path', { className: 'train__trunk', d: 'M1136,' + (y - 5) + 'l8,5l-8,5' }),
      e('text', { className: 'train__cap', x: 60, y: y - 16, 'text-anchor': 'start' }, 'origin/main'),
      e('text', { className: 'train__cap', x: 1148, y: y - 16, 'text-anchor': 'end', fill: 'var(--amber)' }, 'main'),
      TRAIN.map(function (id, i) {
        var x = x0 + i * step;
        var n = byId[id] || { c: 'o' };
        var p = PROJECTS[id] || {};
        var hot = s.hot === id || s.selected === id;
        return e('g', {
          key: id + i, className: 'commit' + (hot ? ' is-hot' : ''),
          'data-id': id, tabIndex: '0', role: 'button',
          'aria-label': 'Open ' + (p.name || id) + ' (merged to main)',
          onMouseEnter: function () { store.set({ hot: id }); },
          onMouseLeave: function () { store.set({ hot: null }); },
          onFocus: function () { store.set({ hot: id }); },
          onBlur: function () { store.set({ hot: null }); },
          onClick: function () { go(id); },
          onKeyDown: function (ev) {
            if (ev.key === 'Enter' || ev.key === ' ') { ev.preventDefault(); go(id); }
          }
        },
          e('rect', { x: x - 78, y: y - 76, width: 156, height: 168, fill: 'transparent' }),
          e('path', { className: 'train__branch', d: 'M' + (x - 92) + ',' + (y - 62) + 'C' + (x - 54) + ',' + (y - 62) + ' ' + (x - 40) + ',' + y + ' ' + (x - 9) + ',' + y }),
          e('circle', { className: 'train__tip', cx: x - 92, cy: y - 62, r: 4.5 }),
          e('circle', { className: 'train__commit tc--' + n.c, cx: x, cy: y, r: 9 }),
          e('text', { className: 'train__idx', x: x, y: y + 40, 'text-anchor': 'middle' }, '#' + pad2(indexOf[id] + 1)),
          e('text', { className: 'train__label', x: x, y: y + 62, 'text-anchor': 'middle' }, (p.name || id).toUpperCase())
        );
      })
    );
  }

  /* ADR-0003 step 2: inline selection chip. Tapping a ring while the work
     section is off-screen raises a chip inside .stage ("03/12 Vector · View
     ↓") instead of auto-scrolling; tapping the chip scrolls to the work
     section (home of the step-3 slider). Selection persists. */
  function initSelChip() {
    var stage = document.getElementById('stage');
    var work = document.getElementById('work');
    if (!stage || !work) return;
    var chip = document.createElement('button');
    chip.className = 'sel-chip';
    chip.type = 'button';
    chip.hidden = true;
    stage.appendChild(chip);
    function workInView() {
      var r = work.getBoundingClientRect();
      return r.top < window.innerHeight && r.bottom > 0;
    }
    function render() {
      var id = store.selected;
      var p = id ? PROJECTS[id] : null;
      if (!id || !p) { chip.hidden = true; return; }
      var label = pad2(indexOf[id] + 1) + '/' + pad2(ORDER.length) + ' ' + (p.name || id);
      chip.textContent = label + ' · View ↓';
      chip.setAttribute('aria-label', label + ' — view in the work section below');
      chip.hidden = workInView();
    }
    store.subscribe(render);
    window.addEventListener('scroll', render, { passive: true });
    window.addEventListener('resize', render);
    chip.addEventListener('click', function () {
      try {
        work.scrollIntoView({ behavior: reduced ? 'auto' : 'smooth', block: 'start' });
      } catch (err) {
        work.scrollIntoView();
      }
    });
    render();
  }

  function mount() {
    var svg = document.getElementById('emblem');
    var sliderRoot = document.getElementById('slider-root');
    var train = document.getElementById('train');
    var tip = document.getElementById('tip');
    if (svg) {
      svg.setAttribute('viewBox', (GRID.view || []).join(' '));
      svg.setAttribute('preserveAspectRatio', 'xMidYMid meet');
    }
    function render(comp, node) {
      if (!node) return;
      try {
        if (ReactDOM.createRoot) ReactDOM.createRoot(node).render(comp);
        else ReactDOM.render(comp, node);
      } catch (err) {
        if (ReactDOM.render) ReactDOM.render(comp, node);
      }
    }
    if (svg) render(e(Emblem, null), svg);
    if (sliderRoot) render(e(Slider, null), sliderRoot);
    if (train) render(e(Train, null), train);
    if (tip) {
      var renderTip = function () {
        var id = store.hot;
        if (!id || !byId[id]) { tip.classList.remove('is-on'); tip.innerHTML = ''; return; }
        var p = PROJECTS[id] || {};
        var v = GRID.view;
        var n = byId[id];
        var py = (n.y - v[1]) / v[3] * 100;
        tip.innerHTML =
          '<span class="tip__idx">' + pad2(indexOf[id] + 1) + '</span>' +
          '<span class="tip__name">' + escapeHtml(p.name || id) + '</span>' +
          '<span class="tip__tag">' + escapeHtml(p.tagline || '') + '</span>' +
          '<span class="tip__cta">View ↓</span>';
        tip.classList.toggle('tip--below', py < 26);
        tip.classList.add('is-on');
        positionTip(id);
      };
      store.subscribe(renderTip);
      renderTip();
    }
    initSelChip();
    chrome();
  }

  function escapeHtml(s) {
    return String(s).replace(/[&<>"']/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c];
    });
  }

  function positionTip(id) {
    var tip = document.getElementById('tip');
    var stage = document.querySelector('.stage');
    if (!tip || !id || !byId[id]) return;
    var n = byId[id];
    var v = GRID.view;
    var px = (n.x - v[0]) / v[2] * 100;
    var py = (n.y - v[1]) / v[3] * 100;
    var sw = stage ? stage.clientWidth : 0, sh = stage ? stage.clientHeight : 0;
    var nx = px / 100 * sw, ny = py / 100 * sh;
    var tw = tip.offsetWidth, th = tip.offsetHeight, pad = 6;
    var shift = 0, left = nx - tw / 2;
    if (left < -pad) shift = -pad - left;
    else if (left + tw > sw + pad) shift = sw + pad - (left + tw);
    var vshift = 0;
    if (py < 26) { if (ny + th + 22 > sh) vshift = sh - (ny + th + 22); }
    else if (ny - th - 26 < 0) { vshift = 26 + th - ny; }
    tip.style.left = nx + 'px';
    tip.style.top = ny + 'px';
    tip.style.marginLeft = shift + 'px';
    tip.style.marginTop = vshift + 'px';
  }
  function chrome() {
    document.querySelectorAll('[data-bind="since"]').forEach(function (el) {
      el.textContent = CFG.collective.since;
    });
    document.querySelectorAll('[data-bind="count"]').forEach(function (el) { el.textContent = ORDER.length; });
    var stacks = {};
    ORDER.forEach(function (id) { ((PROJECTS[id] || {}).stack || []).forEach(function (s) { stacks[s] = 1; }); });
    document.querySelectorAll('[data-bind="techcount"]').forEach(function (el) { el.textContent = Object.keys(stacks).length + '+'; });
    var tr = document.querySelector('[data-bind="tracecount"]');
    if (tr) tr.textContent = (GRID.traces || []).length;
    document.querySelectorAll('[data-bind="year"]').forEach(function (el) {
      if (el.tagName === 'SPAN' && el.closest('.footer__bar')) el.textContent = new Date().getFullYear();
    });

    var nav = document.getElementById('nav');
    var bar = document.querySelector('.progress__bar');
    function onScroll() {
      var sc = window.scrollY || document.documentElement.scrollTop;
      if (nav) nav.classList.toggle('is-stuck', sc > 12);
      var h = document.documentElement.scrollHeight - window.innerHeight;
      if (bar) bar.style.transform = 'scaleX(' + (h > 0 ? sc / h : 0) + ')';
    }
    window.addEventListener('scroll', onScroll, { passive: true });
    onScroll();

    if ('IntersectionObserver' in window && !reduced) {
      var io = new IntersectionObserver(function (entries) {
        entries.forEach(function (en) {
          if (en.isIntersecting) { en.target.classList.add('in'); io.unobserve(en.target); }
        });
      }, { rootMargin: '0px 0px -12% 0px', threshold: 0.08 });
      document.querySelectorAll('.reveal').forEach(function (el) { io.observe(el); });
    } else {
      document.querySelectorAll('.reveal').forEach(function (el) { el.classList.add('in'); });
    }

    var copy = document.querySelector('[data-copy]');
    if (copy) {
      copy.addEventListener('click', function () {
        var text = copy.dataset.copy;
        var done = function () {
          copy.classList.add('is-done');
          var lbl = copy.querySelector('.copy__label');
          if (lbl) { var old = lbl.textContent; lbl.textContent = 'copied'; setTimeout(function () { lbl.textContent = old; copy.classList.remove('is-done'); }, 1600); }
        };
        if (navigator.clipboard) navigator.clipboard.writeText(text).then(done, done);
        else done();
      });
    }

    var menu = document.querySelector('[data-menu]');
    if (menu) {
      menu.addEventListener('click', function () {
        var open = document.body.classList.toggle('menu-open');
        menu.setAttribute('aria-expanded', open ? 'true' : 'false');
      });
      document.querySelectorAll('#nav a').forEach(function (a) {
        a.addEventListener('click', function () {
          document.body.classList.remove('menu-open');
          menu.setAttribute('aria-expanded', 'false');
        });
      });
    }

    document.addEventListener('keydown', function (ev) {
      if (ev.key === 'Escape') {
        store.set({ hot: null, selected: null });
      }
    });

    svgDimSync();
  }

  function svgDimSync() {
    /* Keep emblem focus class in sync when store changes (React sets node classes). */
    store.subscribe(function () {
      var svg = document.getElementById('emblem');
      if (!svg) return;
      var active = store.hot || store.selected;
      svg.classList.toggle('is-focused', !!active);
      /* Sync commit highlight for non-React query paths (QA uses classes). */
      document.querySelectorAll('.commit').forEach(function (g) {
        g.classList.toggle('is-hot', g.dataset.id === store.hot || g.dataset.id === store.selected);
      });
    });
  }

  window.GuildEmblem = {
    select: selectProject, grid: GRID,
    slugFor: function (id) { return SLUGS[id]; },
    pageUrl: pageUrl
  };

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', mount);
  else mount();
})();
