/* Rendering + interaction: emblem, cards, panel, merge train, nav, reveals. */
(function () {
  'use strict';

  var CFG = window.GUILD || {};
  var GRID = window.GUILD_GRID || {};
  var PROJECTS = CFG.projects || {};
  var ORDER = CFG.order || GRID.nodes.map(function (n) { return n.id; });
  var NS = 'http://www.w3.org/2000/svg';

  var NODE_CLICK = CFG.nodeClickBehavior || 'panel';

  var reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  var byId = {};
  GRID.nodes.forEach(function (n) { byId[n.id] = n; });
  var indexOf = {};
  ORDER.forEach(function (id, i) { indexOf[id] = i; });
  var pad2 = function (n) { return String(n).padStart(2, '0'); };

  function el(tag, attrs, text) {
    var e = document.createElementNS(NS, tag);
    for (var k in attrs) e.setAttribute(k, attrs[k]);
    if (text != null) e.textContent = text;
    return e;
  }

  var svg = document.getElementById('emblem');
  if (!svg) return;
  svg.setAttribute('viewBox', GRID.view.join(' '));
  svg.setAttribute('preserveAspectRatio', 'xMidYMid meet');

  var gHalos = el('g', { 'class': 'layer layer--halos' });
  var gTraces = el('g', { 'class': 'layer layer--traces' });
  var gSparks = el('g', { 'class': 'layer layer--sparks' });
  var gNodes = el('g', { 'class': 'layer layer--nodes' });
  [gHalos, gTraces, gSparks, gNodes].forEach(function (g) { svg.appendChild(g); });

  var stroke = GRID.stroke;
  var rMid = (GRID.rIn + GRID.rOut) / 2;
  var rBand = GRID.rOut - GRID.rIn;

  var traceEls = [], haloEls = [];
  GRID.traces.forEach(function (t) {
    var cls = 'trace trace--' + t.c;
    var halo = el('path', { d: t.d, 'class': cls + ' trace--halo', 'stroke-width': stroke * 2.6 });
    var line = el('path', { d: t.d, 'class': cls });
    halo.dataset.i = t.i; line.dataset.i = t.i;
    halo.setAttribute('stroke-linecap', 'round');
    line.setAttribute('stroke-linecap', 'round');
    line.setAttribute('stroke-linejoin', 'round');
    gHalos.appendChild(halo); gTraces.appendChild(line);
    traceEls.push(line); haloEls.push(halo);
  });

  var nodeEls = {};
  ORDER.forEach(function (id) {
    var n = byId[id]; if (!n) return;
    var p = PROJECTS[id] || {};
    var g = el('g', {
      'class': 'node node--' + n.c + ' node--' + id,
      'data-id': id,
      tabindex: '0',
      role: 'button',
      'aria-label': (p.name || id) + (p.tagline ? ' — ' + p.tagline : '') + ' (project ' + (indexOf[id] + 1) + ' of ' + ORDER.length + ')'
    });
    g.appendChild(el('circle', { 'class': 'node__halo', cx: n.x, cy: n.y, r: rMid }));
    g.appendChild(el('circle', { 'class': 'node__orbit', cx: n.x, cy: n.y, r: GRID.rOut + 8 }));
    g.appendChild(el('circle', { 'class': 'node__ring', cx: n.x, cy: n.y, r: rMid, 'stroke-width': rBand }));
    g.appendChild(el('circle', { 'class': 'node__hit', cx: n.x, cy: n.y, r: 31 }));
    gNodes.appendChild(g);
    nodeEls[id] = g;
  });

  function intro() {
    if (reduced) return;
    var lens = traceEls.map(function (t) { return t.getTotalLength(); });
    traceEls.forEach(function (t, i) {
      t.style.strokeDasharray = lens[i];
      t.style.strokeDashoffset = lens[i];
    });
    nodeEls && Object.keys(nodeEls).forEach(function (id) { nodeEls[id].classList.add('is-pending'); });
    requestAnimationFrame(function () { requestAnimationFrame(function () {
      traceEls.forEach(function (t, i) {
        var d = Math.min(900, 250 + lens[i] * 2.4);
        t.style.transition = 'stroke-dashoffset ' + d + 'ms cubic-bezier(.25,.7,.25,1) ' + (i % 12) * 26 + 'ms';
        t.style.strokeDashoffset = 0;
      });
      setTimeout(function () {
        traceEls.forEach(function (t) { t.style.transition = ''; t.style.strokeDasharray = ''; t.style.strokeDashoffset = ''; });
        Object.keys(nodeEls).forEach(function (id, i) {
          var g = nodeEls[id];
          setTimeout(function () { g.classList.remove('is-pending'); g.classList.add('is-in'); }, i * 55);
        });
        svg.classList.add('is-ready');
        setTimeout(bootPulse, 620);
      }, 1500);
    }); });
  }

  function bootPulse() {
    if (reduced) return;
    var hub = 'n1';
    (GRID.adjacency[hub] || []).forEach(function (e) { spark(e[0], e[1], 900); });
  }

  function spark(i, from, dur) {
    var t = traceEls[i];
    if (!t) return;
    var L = t.getTotalLength();
    if (!L) return;
    var run = 24;
    if (L < run * 1.4) run = L * 0.4;
    var s = el('path', {
      d: GRID.traces[i].d,
      'class': 'spark spark--' + GRID.traces[i].c,
      'stroke-dasharray': run + ' ' + L
    });
    gSparks.appendChild(s);
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

  var state = { hot: null, selected: null };

  function tracesOf(id) {
    return (GRID.adjacency[id] || []).map(function (e) { return e[0]; });
  }

  function paint() {
    var active = state.hot || state.selected;
    svg.classList.toggle('is-focused', !!active);
    var lit = {};
    if (active) tracesOf(active).forEach(function (i) { lit[i] = 1; });
    GRID.traces.forEach(function (t) {
      var on = !!lit[t.i];
      traceEls[t.i].classList.toggle('is-lit', on);
      haloEls[t.i].classList.toggle('is-lit', on);
    });
    Object.keys(nodeEls).forEach(function (id) {
      var g = nodeEls[id];
      g.classList.toggle('is-hot', id === state.hot);
      g.classList.toggle('is-selected', id === state.selected);
      var near = active && (id === active || tracesOf(active).some(function (i) {
        return GRID.traces[i].a === id || GRID.traces[i].b === id;
      }));
      g.classList.toggle('is-near', !!near && id !== active);
    });
    syncCards();
  }

  function setHot(id) { state.hot = id; paint(); if (id) showTip(id); else hideTip(); }

  var stage = document.querySelector('.stage');
  var tip = document.getElementById('tip');

  function showTip(id) {
    var n = byId[id], p = PROJECTS[id] || {};
    if (!n || !tip) return;
    var v = GRID.view;
    var px = (n.x - v[0]) / v[2] * 100;
    var py = (n.y - v[1]) / v[3] * 100;
    tip.innerHTML =
      '<span class="tip__idx">' + pad2(indexOf[id] + 1) + '</span>' +
      '<span class="tip__name">' + (p.name || id) + '</span>' +
      '<span class="tip__tag">' + (p.tagline || '') + '</span>' +
      '<span class="tip__cta">Open project ↗</span>';
    tip.classList.toggle('tip--below', py < 26);
    tip.classList.add('is-on');

    var sw = stage ? stage.clientWidth : 0, sh = stage ? stage.clientHeight : 0;
    var nx = px / 100 * sw, ny = py / 100 * sh;
    var tw = tip.offsetWidth, th = tip.offsetHeight, pad = 6;
    var shift = 0, left = nx - tw / 2;
    if (left < -pad) shift = -pad - left;
    else if (left + tw > sw + pad) shift = sw + pad - (left + tw);
    var vshift = 0;
    if (py < 26) {
      if (ny + th + 22 > sh) vshift = sh - (ny + th + 22);
    } else if (ny - th - 26 < 0) {
      vshift = 26 + th - ny;
    }
    tip.style.left = nx + 'px';
    tip.style.top = ny + 'px';
    tip.style.marginLeft = shift + 'px';
    tip.style.marginTop = vshift + 'px';
  }
  function hideTip() { if (tip) tip.classList.remove('is-on'); }

  var panel = document.getElementById('panel');
  var sheet = panel && panel.querySelector('.panel__sheet');

  function openPanel(id) {
    var p = PROJECTS[id] || {};
    var wasOpen = !!(panel && panel.classList.contains('is-open'));
    select(id, true);
    if (NODE_CLICK === 'direct' && p.url) { window.open(p.url, '_blank', 'noopener'); return; }
    if (!panel) return;
    panel.querySelector('[data-bind="idx"]').textContent = 'Node ' + pad2(indexOf[id] + 1) + ' / ' + pad2(ORDER.length);
    panel.querySelector('[data-bind="name"]').textContent = p.name || id;
    panel.querySelector('[data-bind="tagline"]').textContent = p.tagline || '';
    panel.querySelector('[data-bind="blurb"]').textContent = p.blurb || '';
    panel.querySelector('[data-bind="year"]').textContent = p.year || '—';
    var status = panel.querySelector('[data-bind="status"]');
    status.textContent = p.status || 'stable';
    status.dataset.status = p.status || 'stable';
    var chips = panel.querySelector('[data-bind="stack"]');
    chips.innerHTML = (p.stack || []).map(function (s) { return '<li>' + s + '</li>'; }).join('');
    var swatch = panel.querySelector('[data-bind="swatch"]');
    swatch.className = 'panel__swatch panel__swatch--' + (byId[id].c === 'w' ? 'w' : 'o');

    [['visit', p.url], ['repo', p.repo], ['docs', p.docs]].forEach(function (pair) {
      var a = panel.querySelector('[data-bind="' + pair[0] + '"]');
      if (!a) return;
      if (pair[1]) { a.href = pair[1]; a.hidden = false; } else { a.hidden = true; }
    });

    var pos = panel.querySelector('[data-bind="pos"]');
    pos.textContent = pad2(indexOf[id] + 1) + ' / ' + pad2(ORDER.length);
    if (wasOpen && sheet && sheet.animate && !reduced) {
      sheet.animate([{ opacity: 1, transform: 'translateY(0)' }, { opacity: 0, transform: 'translateY(-8px)' }],
        { duration: 140, easing: 'ease-in' }).finished.then(function () {
        sheet.animate([{ opacity: 0, transform: 'translateY(10px)' }, { opacity: 1, transform: 'translateY(0)' }],
          { duration: 280, easing: 'cubic-bezier(.2,.8,.3,1)' });
      }).catch(function () {});
    }
    panel.classList.add('is-open');
    panel.setAttribute('aria-hidden', 'false');
    document.body.classList.add('panel-open');
    document.querySelectorAll('.card').forEach(function (c) {
      c.classList.toggle('is-active', c.dataset.id === id);
    });
    if (sheet) sheet.focus({ preventScroll: true });
  }

  function closePanel() {
    if (!panel) return;
    panel.classList.remove('is-open');
    panel.setAttribute('aria-hidden', 'true');
    document.body.classList.remove('panel-open');
    state.selected = null;
    paint();
  }

  function step(delta) {
    var cur = state.selected || ORDER[0];
    var i = (indexOf[cur] + delta + ORDER.length) % ORDER.length;
    openPanel(ORDER[i]);
  }

  function select(id, quiet) {
    state.selected = id;
    paint();
    if (!quiet && !reduced) {
      (GRID.adjacency[id] || []).forEach(function (e) {
        var len = GRID.traces[e[0]].l || 200;
        spark(e[0], e[1], Math.max(320, Math.min(900, len * 1.1)));
      });
    }
  }

  svg.addEventListener('click', function (ev) {
    if (ev.target === svg || ev.target.classList.contains('layer')) closePanel();
  });

  Object.keys(nodeEls).forEach(function (id) {
    var g = nodeEls[id];
    g.addEventListener('mouseenter', function () { setHot(id); });
    g.addEventListener('mouseleave', function () { setHot(null); });
    g.addEventListener('focus', function () { setHot(id); });
    g.addEventListener('blur', function () { setHot(null); });
    g.addEventListener('click', function (ev) {
      if (ev.metaKey || ev.ctrlKey || ev.shiftKey) {
        var p = PROJECTS[id] || {};
        if (p.url) { window.open(p.url, '_blank', 'noopener'); return; }
      }
      openPanel(id);
    });
    g.addEventListener('keydown', function (ev) {
      if (ev.key === 'Enter' || ev.key === ' ') { ev.preventDefault(); openPanel(id); }
      else if (ev.key === 'ArrowRight' || ev.key === 'ArrowDown') {
        ev.preventDefault(); var n1 = ORDER[(indexOf[id] + 1) % ORDER.length]; nodeEls[n1].focus();
      } else if (ev.key === 'ArrowLeft' || ev.key === 'ArrowUp') {
        ev.preventDefault(); var n0 = ORDER[(indexOf[id] - 1 + ORDER.length) % ORDER.length]; nodeEls[n0].focus();
      }
    });
  });

  if (panel) {
    panel.addEventListener('click', function (ev) {

      if (ev.target === panel || ev.target.closest('.panel__close')) closePanel();
    });
    panel.querySelector('[data-bind="prev"]').addEventListener('click', function () { step(-1); });
    panel.querySelector('[data-bind="next"]').addEventListener('click', function () { step(1); });
  }
  document.addEventListener('keydown', function (ev) {
    if (ev.key === 'Escape' && panel && panel.classList.contains('is-open')) closePanel();
    if (panel && panel.classList.contains('is-open') && !ev.metaKey && !ev.ctrlKey) {
      if (ev.key === 'ArrowRight') step(1);
      if (ev.key === 'ArrowLeft') step(-1);
    }
  });

var grid = document.getElementById('cards');

  function renderCards() {
    if (!grid) return;
    grid.innerHTML = ORDER.map(function (id) {
      var p = PROJECTS[id] || {}, n = byId[id] || {};
      var chips = (p.stack || []).slice(0, 3).map(function (s) { return '<li>' + s + '</li>'; }).join('');
      return '' +
        '<li class="card-cell">' +
          '<button class="card card--' + (n.c === 'w' ? 'w' : 'o') + '" data-id="' + id + '" ' +
            'aria-label="Open ' + (p.name || id) + '">' +
            '<span class="card__head">' +
              '<span class="card__idx">' + pad2(indexOf[id] + 1) + '</span>' +
              '<span class="card__pip"></span>' +
              (p.featured ? '<span class="card__flag">flagship</span>' : '') +
            '</span>' +
            '<span class="card__name">' + (p.name || id) + '</span>' +
            '<span class="card__tag">' + (p.tagline || '') + '</span>' +
            '<span class="card__chips"><ul>' + chips + '</ul></span>' +
            '<span class="card__go" aria-hidden="true">Explore<span class="card__arrow">↗</span></span>' +
          '</button>' +
        '</li>';
    }).join('');

    grid.querySelectorAll('.card').forEach(function (card) {
      var id = card.dataset.id;
      card.addEventListener('mouseenter', function () { setHot(id); });
      card.addEventListener('mouseleave', function () { setHot(null); });
      card.addEventListener('focus', function () { setHot(id); });
      card.addEventListener('blur', function () { setHot(null); });
      card.addEventListener('click', function () { openPanel(id); });
    });
  }

  function syncCards() {
    if (grid) grid.querySelectorAll('.card').forEach(function (c) {
      c.classList.toggle('is-hot', c.dataset.id === state.hot);
    });
    commitEls.forEach(function (g) {
      g.classList.toggle('is-hot', g.dataset.id === state.hot || g.dataset.id === state.selected);
    });
  }

  function chrome() {
    var y = document.querySelector('[data-bind="since"]');
    if (y) y.textContent = CFG.collective.since;

    document.querySelectorAll('[data-bind="count"]').forEach(function (e) {
      e.textContent = ORDER.length;
    });
    var stacks = {};
    ORDER.forEach(function (id) { (PROJECTS[id].stack || []).forEach(function (s) { stacks[s] = 1; }); });
    document.querySelectorAll('[data-bind="techcount"]').forEach(function (e) {
      e.textContent = Object.keys(stacks).length + '+';
    });
    var tr = document.querySelector('[data-bind="tracecount"]');
    if (tr) tr.textContent = GRID.traces.length;

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

    if ('IntersectionObserver' in window) {
      var io = new IntersectionObserver(function (entries) {
        entries.forEach(function (en) {
          if (en.isIntersecting) { en.target.classList.add('in'); io.unobserve(en.target); }
        });
      }, { rootMargin: '0px 0px -12% 0px', threshold: 0.08 });
      document.querySelectorAll('.reveal').forEach(function (e) { io.observe(e); });
    } else {
      document.querySelectorAll('.reveal').forEach(function (e) { e.classList.add('in'); });
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
  }

var trainSvg = document.getElementById('train');
  var TRAIN = CFG.mergeTrain || ['n11', 'n9', 'n6', 'n1', 'n5', 'n0'];
  var commitEls = [];

  function renderTrain() {
    if (!trainSvg) return;
    var y = 96, x0 = 190, step = 164;
    var add = function (tag, attrs, text) {
      var e = el(tag, attrs);
      if (text != null) e.textContent = text;
      trainSvg.appendChild(e);
      return e;
    };
    add('path', { 'class': 'train__trunk', d: 'M64,' + y + 'H1144' });
    add('path', { 'class': 'train__trunk', d: 'M1136,' + (y - 5) + 'l8,5l-8,5' });
    add('text', { 'class': 'train__cap', x: 60, y: y - 16, 'text-anchor': 'start' }, 'origin/main');
    add('text', { 'class': 'train__cap', x: 1148, y: y - 16, 'text-anchor': 'end', fill: 'var(--amber)' }, 'main');

    TRAIN.forEach(function (id, i) {
      var x = x0 + i * step;
      var n = byId[id] || { c: 'o' };
      var p = PROJECTS[id] || {};
      var g = el('g', { 'class': 'commit', 'data-id': id, tabindex: '0', role: 'button',
                        'aria-label': 'Open ' + (p.name || id) + ' (merged to main)' });
      g.appendChild(el('rect', { x: x - 78, y: y - 76, width: 156, height: 168, fill: 'transparent' }));
      g.appendChild(el('path', { 'class': 'train__branch',
        d: 'M' + (x - 92) + ',' + (y - 62) + 'C' + (x - 54) + ',' + (y - 62) + ' ' + (x - 40) + ',' + y + ' ' + (x - 9) + ',' + y }));
      g.appendChild(el('circle', { 'class': 'train__tip', cx: x - 92, cy: y - 62, r: 4.5 }));
      var dot = el('circle', { 'class': 'train__commit tc--' + n.c, cx: x, cy: y, r: 9 });
      g.appendChild(dot);
      var idx = el('text', { 'class': 'train__idx', x: x, y: y + 40, 'text-anchor': 'middle' },
        '#' + pad2(indexOf[id] + 1));
      var nm = el('text', { 'class': 'train__label', x: x, y: y + 62, 'text-anchor': 'middle' },
        (p.name || id).toUpperCase());
      g.appendChild(idx); g.appendChild(nm);
      trainSvg.appendChild(g);
      g.addEventListener('mouseenter', function () { setHot(id); });
      g.addEventListener('mouseleave', function () { setHot(null); });
      g.addEventListener('focus', function () { setHot(id); });
      g.addEventListener('blur', function () { setHot(null); });
      g.addEventListener('click', function () { openPanel(id); });
      g.addEventListener('keydown', function (ev) {
        if (ev.key === 'Enter' || ev.key === ' ') { ev.preventDefault(); openPanel(id); }
      });
      commitEls.push(g);
    });
  }

  renderCards();
  renderTrain();
  chrome();
  paint();
  intro();

  window.GuildEmblem = { select: select, open: openPanel, close: closePanel, grid: GRID };
})();
