/* WB shell: rail, run switcher, navigator, module switcher, router, inspector, search, keyboard, print.
   Loads last: every view is registered by the time WB.start() runs. */
(function () {
  'use strict';
  const WB = window.WB;
  const el = WB.el;

  const RAIL = [
    { view: 'front', label: 'Front Page', icon: 'frontpage' },
    { view: 'module', label: 'Analysis', icon: 'analysis' },
    { view: 'model', label: 'Model', icon: 'model' },
    { view: 'fit', label: 'Portfolio Fit', icon: 'fit' },
    { view: 'evidence', label: 'Evidence', icon: 'evidence' },
    { view: 'limitations', label: 'Limitations', icon: 'limitations' },
    { view: 'system', label: 'Design system', icon: 'system' },
  ];
  const shell = { root: null, rail: null, nav: null, canvas: null, insp: null, layers: null, live: null, current: null, returnEl: null, layer: null };
  WB.shell = shell;

  /* ---------- routing ---------- */
  WB.parseHash = function (hash) {
    const parts = String(hash || '').replace(/^#\/?/, '').split('/').filter(Boolean).map((p) => {
      try {
        return decodeURIComponent(p);
      } catch (e) {
        return p;
      }
    });
    if (!parts.length) return { run: null, view: null, id: null, anchor: null };
    const run = parts[0];
    const view = parts[1] || 'front';
    if (view === 'module') return { run, view, id: parts[2] || null, anchor: parts[3] || null };
    return { run, view, id: null, anchor: parts[2] || null };
  };
  WB.navigate = (href) => {
    location.hash = href.replace(/^#/, '');
  };
  WB.announce = (msg) => {
    if (shell.live) shell.live.textContent = msg;
  };

  function viewAvailability(name, run) {
    const v = WB.views[name];
    if (!v) return { ok: false, reason: 'Not built yet in this mock.' };
    const a = v.available ? v.available(run) : true;
    return a === true ? { ok: true } : { ok: false, reason: typeof a === 'string' ? a : 'Not available in this run.' };
  }
  WB.viewAvailability = viewAvailability;

  function stateMessage(canvas, title, text, extra, withIssuer) {
    canvas.appendChild(
      el('div', { class: 'view view-state' }, [
        el('div', { class: 'm-bar' }, el('div', { class: 'm-title' }, [withIssuer ? WB.issuerNode({ sep: true }) : null, el('h1', null, title)])),
        el('div', { class: 'state-body' }, [WB.conditionLine(text), extra || null]),
      ])
    );
  }

  let lastKey = null;
  let booted = false;
  function route(force) {
    const canvas = shell.canvas;
    let h = WB.parseHash(location.hash);
    if (!h.run) {
      history.replaceState(null, '', '#/' + WB.DEFAULT_RUN + '/front');
      h = WB.parseHash(location.hash);
    }
    const key = [h.run, h.view, h.id].join('|') + '|' + (WB.state.honest ? 'h' : '');
    if (!force && key === lastKey && WB.run && WB.run._id === h.run) {
      WB.scrollToAnchor(h.anchor);
      return;
    }
    lastKey = key;
    delete document.documentElement.dataset.ready;
    const prevScroll = force ? canvas.scrollTop : 0;
    const run = WB.runIds.includes(h.run) ? WB.loadRun(h.run) : null;
    canvas.replaceChildren();
    WB.clearRefs();
    WB.resetUnresolved();
    WB.page = { outline: [], gapModules: [], title: '' };
    WB.setNavExtra(null);
    clearSelection();
    if (!run) {
      WB.run = WB.run || WB.loadRun(WB.DEFAULT_RUN);
      stateMessage(
        canvas,
        'Run not found',
        'No run named "' + h.run + '" is embedded in this file.',
        el('ul', { class: 'state-list' }, WB.runIds.map((id) => el('li', null, el('a', { href: '#/' + id + '/front' }, id))))
      );
      renderChrome(h, null);
      finish(h, 0, force);
      return;
    }
    if (!WB.run || WB.run._id !== run._id) {
      WB.run = run;
      resetInspector();
    }
    const name = h.view;
    const av = viewAvailability(name, run);
    const known = RAIL.find((r) => r.view === name);
    if (!WB.views[name] && known) {
      stateMessage(canvas, known.label, 'This view is not built yet in this mock.');
    } else if (!WB.views[name]) {
      stateMessage(canvas, 'View not found', 'This Report has no view called "' + name + '". Views: ' + Object.keys(WB.views).join(', ') + '.');
    } else if (!av.ok) {
      stateMessage(canvas, WB.views[name].title, av.reason, null, true);
    } else {
      try {
        WB.views[name].render(canvas, run, { id: h.id, anchor: h.anchor });
      } catch (err) {
        canvas.appendChild(el('div', { class: 'view view-state' }, el('div', { class: 'state-body' }, WB.conditionLine('This view failed to render: ' + err.message))));
        throw err;
      }
    }
    renderChrome(h, run);
    finish(h, prevScroll, force);
  }
  function finish(h, prevScroll, force) {
    const canvas = shell.canvas;
    if (h.anchor) {
      requestAnimationFrame(() => WB.scrollToAnchor(h.anchor));
    } else canvas.scrollTop = prevScroll || 0;
    canvas.scrollLeft = 0;
    WB.initRovingIn(canvas);
    updateSpy();
    if (booted && !force) canvas.focus({ preventScroll: true });
    const de = document.documentElement.dataset;
    de.run = WB.run ? WB.run._id : '';
    de.view = h.view || '';
    de.plan = WB.run ? (WB.run.plan || []).join(',') : '';
    de.views = WB.run ? Object.keys(WB.views).filter((n) => viewAvailability(n, WB.run).ok).join(',') : '';
    de.ready = '1';
    booted = true;
  }
  WB.rerender = () => route(true);

  /* ---------- chrome: rail, navigator, title ---------- */
  function renderChrome(h, run) {
    renderRail(h, run);
    renderNavigator(h, run);
    const meta = run ? WB.runMeta(run) : null;
    const v = WB.views[h.view];
    let t = v ? v.title : 'Report';
    if (h.view === 'module' && h.id) t = WB.moduleName(h.id);
    document.title = (meta ? meta.issuer + ' · ' : '') + t + ' · RBOT Workbench';
    shell.root.dataset.view = h.view || '';
  }

  function railItem(item, h, run) {
    const av = run ? viewAvailability(item.view, run) : { ok: false, reason: 'No run' };
    const active = h.view === item.view;
    let href = WB.href(item.view, null, run && run._id);
    if (item.view === 'module') {
      const first = run && (run.plan || [])[0];
      href = WB.href('module' + (first ? '/' + first : ''), null, run && run._id);
    }
    const tip = av.ok ? item.label : item.label + ': ' + av.reason.replace(/^Not built yet in this mock\.$/, 'Not built yet in this mock');
    const a = el(
      'a',
      {
        class: 'rail-btn' + (active ? ' is-active' : '') + (av.ok ? '' : ' is-disabled'),
        href: av.ok ? href : false,
        role: av.ok ? false : 'link',
        'aria-disabled': av.ok ? false : 'true',
        'aria-current': active ? 'page' : false,
        'aria-label': av.ok ? item.label : item.label + ', ' + av.reason.replace(/\.$/, '').toLowerCase(),
        'data-tip': tip,
        tabindex: av.ok ? false : '0',
      },
      [WB.icon(item.icon, { size: 18 })]
    );
    if (!av.ok) a.addEventListener('click', (e) => e.preventDefault());
    return a;
  }
  function railButton(icon, label, handler, extra) {
    const b = el('button', { type: 'button', class: 'rail-btn rail-act', 'aria-label': label, 'data-tip': label, 'aria-pressed': extra && extra.pressed != null ? String(extra.pressed) : false }, WB.icon(icon, { size: 18 }));
    b.addEventListener('click', handler);
    return b;
  }
  function renderRail(h, run) {
    const rail = shell.rail;
    rail.replaceChildren(
      el('div', { class: 'rail-logo', role: 'img', 'aria-label': 'State Street Investment Management', 'data-tip': 'State Street Investment Management' }),
      el('div', { class: 'rail-dest' }, RAIL.map((it) => railItem(it, h, run))),
      el('div', { class: 'rail-sp' }),
      el('div', { class: 'rail-act-g' }, [
        railButton('search', 'Search the Report (/)', () => openSearch()),
        railButton('help', 'How to read a figure (?)', () => openHelp()),
        railButton('print', 'Print', () => window.print()),
        railButton('sidebar', shell.root.dataset.nav === 'open' ? 'Close the navigator' : 'Open the navigator', () => toggleNav(), { pressed: shell.root.dataset.nav === 'open' }),
      ])
    );
  }
  function toggleNav(open) {
    const next = open == null ? shell.root.dataset.nav !== 'open' : open;
    shell.root.dataset.nav = next ? 'open' : 'closed';
    const b = WB.qs('.rail-act-g .rail-btn:last-child', shell.rail);
    if (b) {
      b.setAttribute('aria-pressed', String(next));
      b.setAttribute('aria-label', next ? 'Close the navigator' : 'Open the navigator');
      b.dataset.tip = next ? 'Close the navigator' : 'Open the navigator';
    }
  }

  let navExtra = null;
  WB.setNavExtra = function (node) {
    navExtra = node;
    const slot = WB.qs('.nav-extra', shell.nav);
    if (slot) slot.replaceChildren(node || '');
  };

  function renderNavigator(h, run) {
    const nav = shell.nav;
    nav.replaceChildren();
    if (!run) return;
    const meta = WB.runMeta(run);
    const issuer = el('button', { type: 'button', class: 'nav-issuer', 'aria-haspopup': 'dialog', 'aria-expanded': shell.layer && shell.layer.id === 'runs' ? 'true' : 'false', 'aria-label': 'Switch run. Current: ' + meta.issuer + ', ' + meta.pathway }, [
      el('span', { class: 'ni-top' }, [el('span', { class: 'ni-name' }, meta.issuer.replace(/, Inc\.?$/, '')), WB.icon('chevron-down', { size: 12, stroke: 1.8 })]),
      el('span', { class: 'ni-meta num' }, [meta.issuerId, meta.asOf ? ' · ' + WB.fmtDate(meta.asOf) : ''].join('')),
      el('span', { class: 'ni-sub' }, meta.pathway + ' · ' + (meta.depth === 'quick' ? 'Quick' : 'Full') + ' depth'),
      el('span', { class: 'ni-tags' }, meta.tags.map((t) => el('span', { class: 'rtag rtag-' + t.toLowerCase().replace(/\s+/g, '-') }, t))),
    ]);
    issuer.addEventListener('click', () => openRunSwitcher(issuer));
    nav.appendChild(issuer);
    const find = el('button', { type: 'button', class: 'nav-find' }, [WB.icon('search', { size: 13 }), el('span', null, 'Find a module, figure or source'), el('kbd', null, '/')]);
    find.addEventListener('click', () => openSearch());
    nav.appendChild(find);

    // modules
    const plan = (run.plan || []).filter((id) => (WB.step(id) || {}).kind === 'module');
    const rows = plan.map((id, i) => ({ id, i, status: WB.stepStatus(id) }));
    const counts = { all: rows.length, limitations: 0, pass: 0, blocked: 0, notrun: 0 };
    rows.forEach((r) => counts[r.status]++);
    const filter = WB.state.navFilter;
    const chipDefs = [
      ['all', 'All', counts.all, ''],
      ['limitations', 'With limitations', counts.limitations, 'tone-cau'],
      ['pass', 'Pass', counts.pass, 'tone-pos'],
      ['blocked', 'Blocked', counts.blocked, 'tone-neg'],
    ];
    const chips = el('div', { class: 'nav-chips', role: 'group', 'aria-label': 'Filter modules' }, chipDefs.map(([k, label, n, tone]) => {
      const ic = { limitations: 'status-limited', pass: 'status-pass', blocked: 'status-blocked' }[k];
      const b = el('button', { type: 'button', class: 'nchip ' + tone + (filter === k ? ' on' : '') + (!n && k !== 'all' ? ' zero' : ''), 'aria-pressed': filter === k ? 'true' : 'false', title: label + ': ' + n }, [ic ? WB.icon(ic, { size: 12, stroke: 1.8 }) : null, el('span', { class: 'nc-l' }, label), el('span', { class: 'num' }, String(n))]);
      b.addEventListener('click', () => {
        WB.state.navFilter = k;
        renderNavigator(WB.parseHash(location.hash), WB.run);
        const again = WB.qs('.nchip.on', shell.nav);
        if (again) again.focus();
      });
      return b;
    }));
    nav.appendChild(el('div', { class: 'nav-group-h' }, el('span', { class: 'nav-h' }, 'Analysis \u00B7 ' + plan.length)));
    nav.appendChild(chips);
    const shown = rows.filter((r) => filter === 'all' || r.status === filter);
    // a status icon spends signal colour, so it shows only where a row departs from the run's most common status (the norm);
    // the status word stays in each row's accessible name and tooltip, and in the module view. Ties go to the first of the order below.
    const norm = ['limitations', 'pass', 'notrun', 'blocked'].reduce((best, k) => (counts[k] > (counts[best] || 0) ? k : best), 'limitations');
    const ul = el('ul', { class: 'nav-modules' });
    shown.forEach((r) => {
      const active = h.view === 'module' ? (h.id || plan[0]) === r.id : (h.view === 'model' && r.id === 'MODEL') || (h.view === 'fit' && r.id === 'FIT');
      const a = el(
        'a',
        { class: 'nav-row' + (active ? ' is-active' : ''), href: WB.moduleHref(r.id), 'aria-current': active ? 'page' : false, title: WB.moduleName(r.id) + ': ' + WB.STATUS_WORD[r.status], 'aria-label': WB.moduleName(r.id) + ', ' + r.id + ': ' + WB.STATUS_WORD[r.status] },
        [
          el('span', { class: 'nr-n num' }, String(r.i + 1)),
          el('span', { class: 'nr-i tone-' + WB.STATUS_TONE[r.status] }, r.status === norm ? null : WB.icon(WB.STATUS_ICON[r.status], { size: 14, stroke: 1.8, label: WB.STATUS_WORD[r.status] })),
          el('span', { class: 'nr-t' }, WB.moduleName(r.id)),
          el('span', { class: 'nr-c num' }, r.id),
        ]
      );
      ul.appendChild(el('li', null, a));
    });
    if (!shown.length) ul.appendChild(el('li', { class: 'nav-none' }, 'No module matches this filter.'));
    nav.appendChild(ul);

    // on this page
    const outline = el('nav', { class: 'nav-outline', 'aria-label': 'On this page' });
    nav.appendChild(el('div', { class: 'nav-slot' }, outline));
    WB.renderOutline = function () {
      outline.replaceChildren();
      const items = WB.page.outline || [];
      if (!items.length) return;
      outline.appendChild(el('div', { class: 'nav-h' }, 'On this page'));
      items.forEach((it) => {
        const a = el('a', { class: 'ol-i' + (it.na ? ' na' : ''), href: WB.href(h.view + (h.id ? '/' + h.id : ''), it.id.replace(/^p-/, ''), run._id), 'data-ol': it.id }, [it.label, it.na ? el('i', null, 'condition') : null]);
        outline.appendChild(a);
      });
    };
    WB.renderOutline();
    nav.appendChild(el('div', { class: 'nav-extra' }, navExtra || null));
    nav.appendChild(el('p', { class: 'nav-foot' }, 'Judgements are illustrative; synthetic values are marked.'));
  }

  /* scroll spy over the outline */
  function updateSpy() {
    const canvas = shell.canvas;
    const items = WB.qsa('.ol-i', shell.nav);
    if (!items.length) return;
    const top = canvas.getBoundingClientRect().top + 90;
    let cur = items[0];
    for (const it of items) {
      const n = document.getElementById(it.dataset.ol);
      if (n && n.getBoundingClientRect().top <= top) cur = it;
    }
    for (const it of items) {
      const on = it === cur;
      it.classList.toggle('on', on);
      if (on) it.setAttribute('aria-current', 'location');
      else it.removeAttribute('aria-current');
    }
  }

  /* ---------- floating layers ---------- */
  function closeLayer(restore) {
    const l = shell.layer;
    if (!l) return;
    l.node.remove();
    shell.layer = null;
    const iss = WB.qs('.nav-issuer', shell.nav);
    if (iss) iss.setAttribute('aria-expanded', 'false');
    if (restore !== false && l.opener && document.contains(l.opener)) l.opener.focus();
  }
  function openLayer(id, node, opener, opts) {
    closeLayer(false);
    const o = opts || {};
    const wrap = el('div', { class: 'layer layer-' + id + (o.dim ? ' dim' : ''), id: 'layer-' + id }, node);
    wrap.addEventListener('mousedown', (e) => {
      if (e.target === wrap) closeLayer();
    });
    shell.layers.appendChild(wrap);
    shell.layer = { id, node: wrap, opener: opener || document.activeElement };
  }

  function openRunSwitcher(opener) {
    const groups = {};
    WB.runIds.forEach((id) => {
      const r = WB.loadRun(id);
      const m = WB.runMeta(r);
      (groups[m.pathwayKey] = groups[m.pathwayKey] || []).push(m);
    });
    const body = el('div', { class: 'rs', role: 'dialog', 'aria-label': 'Switch run' });
    body.appendChild(el('div', { class: 'rs-h' }, [el('h2', null, 'Runs'), el('span', { class: 'muted' }, WB.runIds.length + ' runs')]));
    const list = el('div', { class: 'rs-list' });
    Object.keys(WB.PATHWAYS).forEach((pk) => {
      if (!groups[pk]) return;
      groups[pk].sort((a, b) => (a.depth === 'full' ? 0 : 1) - (b.depth === 'full' ? 0 : 1) || a.id.localeCompare(b.id));
      list.appendChild(el('div', { class: 'rs-g' }, WB.PATHWAYS[pk]));
      groups[pk].forEach((m) => {
        const cur = WB.run && WB.run._id === m.id;
        const a = el('a', { class: 'rs-row' + (cur ? ' is-active' : ''), href: WB.href('front', null, m.id), 'aria-current': cur ? 'true' : false }, [
          el('span', { class: 'rs-main' }, [el('span', { class: 'rs-issuer' }, m.issuer.replace(/, Inc\.?$/, '')), el('span', { class: 'rs-id num' }, m.id)]),
          el('span', { class: 'ni-tags' }, m.tags.map((t) => el('span', { class: 'rtag rtag-' + t.toLowerCase().replace(/\s+/g, '-') }, t))),
        ]);
        a.addEventListener('click', () => closeLayer(false));
        list.appendChild(a);
      });
    });
    body.appendChild(list);
    const sw = el('button', { type: 'button', class: 'rs-switch', role: 'switch', 'aria-checked': WB.state.honest ? 'true' : 'false' }, [
      el('span', { class: 'sw-track' }, el('span', { class: 'sw-dot' })),
      el('span', { class: 'sw-l' }, [el('strong', null, 'Show the real-run state'), el('span', null, 'Replace the illustrative verdicts with what the live CAOS runs produced: no Recommendation, no Valuation, relative value Unclear, distress gate Not met.')]),
    ]);
    sw.addEventListener('click', () => {
      WB.state.honest = !WB.state.honest;
      sw.setAttribute('aria-checked', String(WB.state.honest));
      WB.rerender();
    });
    body.appendChild(sw);
    openLayer('runs', body, opener, { dim: false });
    const iss = WB.qs('.nav-issuer', shell.nav);
    if (iss) iss.setAttribute('aria-expanded', 'true');
    const first = WB.qs('.rs-row.is-active', body) || WB.qs('.rs-row', body);
    if (first) first.focus();
  }

  /* search / module switcher */
  function buildIndex(run) {
    if (run._index) return run._index;
    const items = [];
    for (const id of run.plan || []) {
      items.push({ type: 'Modules', title: WB.moduleName(id), code: id, sub: WB.moduleQuestion(id), href: WB.moduleHref(id), status: WB.stepStatus(id), hay: (WB.moduleName(id) + ' ' + id + ' ' + WB.moduleQuestion(id)).toLowerCase() });
    }
    const chartHref = (c) => {
      const m = /^front_page:(\d+)$/.exec(c.where);
      if (m) return WB.href('front', 'p-' + WB.cssId(run.front_page + '.' + m[1]), run._id);
      if (c.where === 'model_tab') return WB.href('model');
      const mod = c.where.startsWith('analysis:') ? c.where.slice(9) : (c.tables || []).map((t) => WB.tableOwner(t)).find(Boolean);
      return mod ? WB.href('module/' + mod + '/c-' + WB.cssId(c.chart_id), null, run._id) : WB.href('front');
    };
    for (const c of run.charts || []) items.push({ type: 'Figures', title: WB.chartTitle(c.chart_id), code: 'Chart', sub: '', href: chartHref(c), hay: (WB.chartTitle(c.chart_id) + ' ' + c.chart_id).toLowerCase() });
    for (const [tid, t] of run._tables) {
      // chart twins and Design system specimens are not tables of the Report: the chart itself is listed above
      if (tid.indexOf('@') >= 0 || /^ds\./.test(tid)) continue;
      const href = t.owner === 'RUN_BRIEF' ? WB.href('front') : WB.href('module/' + t.owner + '/t-' + WB.cssId(tid), null, run._id);
      items.push({ type: 'Figures', title: WB.tableTitle(tid), code: t.owner === 'RUN_BRIEF' ? 'BRIEF' : t.owner, sub: WB.moduleName(WB.citeModule(t.owner)), href, hay: (WB.tableTitle(tid) + ' ' + tid).toLowerCase() });
    }
    const srcs = new Map();
    for (const [hid, h] of Object.entries(run.handoffs || {})) {
      for (const c of h.citations || []) {
        srcs.set(c.source, (srcs.get(c.source) || 0) + 1);
        items.push({ type: 'Sources', title: c.source, code: hid + ' ' + c.id, sub: c.excerpt, href: WB.href('evidence', 'ev-' + WB.cssId(hid + '-' + c.id), run._id), cite: true, hay: (c.source + ' ' + c.locator + ' ' + c.excerpt).toLowerCase() });
      }
    }
    run._index = items;
    return items;
  }
  function openSearch() {
    if (!WB.run) return;
    const opener = document.activeElement;
    const index = buildIndex(WB.run);
    const input = el('input', { type: 'text', class: 'sq-in', role: 'combobox', 'aria-expanded': 'true', 'aria-controls': 'sq-list', 'aria-autocomplete': 'list', placeholder: 'modules, figures, sources', 'aria-label': 'Search the Report', autocomplete: 'off', spellcheck: 'false' });
    const list = el('div', { class: 'sq-list', id: 'sq-list', role: 'listbox', 'aria-label': 'Results' });
    const box = el('div', { class: 'sq', role: 'dialog', 'aria-label': 'Search the Report' }, [
      el('div', { class: 'sq-top' }, [WB.icon('search', { size: 16 }), input, el('kbd', null, 'Esc')]),
      list,
    ]);
    let results = [];
    let sel = 0;
    function paint() {
      const q = input.value.trim().toLowerCase();
      const toks = q.split(/\s+/).filter(Boolean);
      const groups = { Modules: [], Figures: [], Sources: [] };
      const cap = { Modules: 8, Figures: 6, Sources: 6 };
      if (!toks.length) {
        index.filter((i) => i.type === 'Modules').slice(0, 8).forEach((i) => groups.Modules.push(i));
      } else {
        const scored = [];
        for (const it of index) {
          if (!toks.every((t) => it.hay.includes(t))) continue;
          const tl = it.title.toLowerCase();
          const s = tl.startsWith(toks[0]) ? 3 : tl.includes(toks[0]) ? 2 : 1;
          scored.push([s, it]);
        }
        scored.sort((a, b) => b[0] - a[0]);
        for (const [, it] of scored) if (groups[it.type].length < cap[it.type]) groups[it.type].push(it);
      }
      results = [];
      list.replaceChildren();
      for (const g of ['Modules', 'Figures', 'Sources']) {
        if (!groups[g].length) continue;
        list.appendChild(el('div', { class: 'sq-g', role: 'presentation' }, g));
        groups[g].forEach((it) => {
          const idx = results.length;
          results.push(it);
          const row = el('a', { class: 'sq-r' + (idx === sel ? ' on' : ''), role: 'option', id: 'sq-' + idx, 'aria-selected': idx === sel ? 'true' : 'false', href: it.href, tabindex: '-1' }, [
            it.status ? el('span', { class: 'sq-i tone-' + WB.STATUS_TONE[it.status] }, WB.icon(WB.STATUS_ICON[it.status], { size: 14, stroke: 1.8 })) : it.cite ? WB.icon(WB.docIcon(it.title), { size: 14 }) : WB.icon(it.type === 'Figures' ? 'chart' : 'evidence', { size: 14 }),
            el('span', { class: 'sq-t' }, [el('span', { class: 'sq-tt' }, it.title), it.sub ? el('span', { class: 'sq-sub' }, it.sub) : null]),
            el('span', { class: 'sq-c num' }, it.code),
          ]);
          row.addEventListener('click', () => closeLayer(false));
          list.appendChild(row);
        });
      }
      if (!results.length) list.appendChild(el('div', { class: 'sq-none' }, 'Nothing matches "' + input.value + '".'));
      if (sel >= results.length) sel = 0;
      mark();
    }
    function mark() {
      WB.qsa('.sq-r', list).forEach((r, i) => {
        const on = i === sel;
        r.classList.toggle('on', on);
        r.setAttribute('aria-selected', on ? 'true' : 'false');
        if (on) {
          input.setAttribute('aria-activedescendant', r.id);
          r.scrollIntoView({ block: 'nearest' });
        }
      });
    }
    input.addEventListener('input', () => {
      sel = 0;
      paint();
    });
    input.addEventListener('keydown', (e) => {
      if (e.key === 'ArrowDown') {
        e.preventDefault();
        sel = Math.min(results.length - 1, sel + 1);
        mark();
      } else if (e.key === 'ArrowUp') {
        e.preventDefault();
        sel = Math.max(0, sel - 1);
        mark();
      } else if (e.key === 'Enter') {
        e.preventDefault();
        const it = results[sel];
        if (it) {
          closeLayer(false);
          WB.navigate(it.href);
        }
      }
    });
    openLayer('search', box, opener, { dim: true });
    paint();
    input.focus();
  }

  function openHelp() {
    const opener = document.activeElement;
    const row = (glyph, name, text) => el('div', { class: 'hk-r' }, [el('span', { class: 'hk-g' }, glyph), el('div', null, [el('strong', null, name), ' ', el('span', null, text)])]);
    const sig = (tone, icon, word) => el('span', { class: 'badge tone-' + tone }, [WB.icon(icon, { size: 12, stroke: 1.8 }), el('span', { class: 'bw' }, word)]);
    const box = el('div', { class: 'hk', role: 'dialog', 'aria-label': 'How to read a figure' }, [
      el('div', { class: 'hk-h' }, [el('h2', null, 'How to read a figure'), el('button', { type: 'button', class: 'btn-x', 'aria-label': 'Close', onclick: () => closeLayer() }, WB.icon('close', { size: 14 }))]),
      el('p', { class: 'hk-lead' }, 'Select any figure, chart mark or chip. Its passport opens in the inspector on the right: where it came from, and what feeds it.'),
      el('h3', null, 'Where a figure comes from'),
      row(WB.mark('cited', { size: 14 }), 'Cited.', 'Read from a document in the Source Pack. The passport shows file, locator and the verbatim excerpt.'),
      row(WB.mark('calculated', { size: 14 }), 'Calculated.', 'Computed by a script from cited inputs. The passport shows the formula, with each input as a chip.'),
      row(WB.mark('synthetic', { size: 14 }), 'Synthetic.', 'TEST DATA invented for the design. Not a fact about the issuer.'),
      row(WB.mark('model', { size: 14 }), 'Model-written.', 'Prose or judgement written by the model. Its figures stay clickable.'),
      row(WB.mark('illustrative', { size: 14 }), 'Illustrative.', 'A judgement no RBOT run has produced yet. Every test run is a design fixture.'),
      row(WB.mark('gap', { size: 14 }), 'n/a.', 'The sources cannot support the figure. It is never zero or blank. A gap id such as G8 opens the reason.'),
      el('p', { class: 'hk-n' }, 'In dense tables the marks are quiet and strengthen on row hover or focus. The shapes differ, so colour is never the only carrier.'),
      el('h3', null, 'Colour is a signal, never alone'),
      el('div', { class: 'hk-sig' }, [sig('pos', 'tick', 'Positive'), sig('cau', 'warn', 'Caution'), sig('neg', 'cross', 'Negative'), sig('neu', 'info', 'No verdict')]),
      el('p', { class: 'hk-n' }, 'Colour follows meaning for the creditor, not arithmetic sign. Every colour comes with an icon or a word. Navy and electric blue mark structure and action, never a verdict.'),
      el('h3', null, 'Module status'),
      el('div', { class: 'hk-sig' }, ['pass', 'limitations', 'blocked', 'notrun'].map((s) => WB.statusChip(s))),
      el('h3', null, 'Numbers'),
      el('p', { class: 'hk-n' }, 'Yields and prices print to 2 decimals, amounts in whole millions, negatives in parentheses, thousands grouped. The passport shows "Served as": the value as the run holds it.'),
      el('h3', null, 'Keys'),
      el('div', { class: 'hk-keys' }, [
        el('span', null, [el('kbd', null, '/'), ' search']),
        el('span', null, [el('kbd', null, '?'), ' this key']),
        el('span', null, [el('kbd', null, 'Tab'), ' rail, navigator, canvas, inspector']),
        el('span', null, [el('kbd', null, '←↑→↓'), ' within a table, chart or group of figures']),
        el('span', null, [el('kbd', null, 'Enter'), ' open passport']),
        el('span', null, [el('kbd', null, 'Esc'), ' back to the figure']),
      ]),
    ]);
    openLayer('help', box, opener, { dim: false });
    WB.qs('.btn-x', box).focus();
  }

  /* ---------- inspector ---------- */
  const insp = { tab: 'source', desc: null, passport: null, history: [], selected: null };
  function resetInspector() {
    insp.desc = null;
    insp.passport = null;
    insp.history = [];
    if (shell.insp) renderInspector();
  }
  /* Below 1360px an inspector with nothing selected is a slim strip: selecting a figure opens it at full width, closing returns to the strip.
     From 1360px up it is always the full pane (the CSS ignores data-insp there). */
  const narrow = () => !window.matchMedia('(min-width: 1360px)').matches;
  function setInspOpen(open) {
    if (shell.root) shell.root.dataset.insp = open ? 'open' : 'closed';
  }
  function clearSelection() {
    if (insp.selected) insp.selected.classList.remove('is-selected');
    insp.selected = null;
    if (shell.insp && insp.desc) {
      insp.desc = null;
      insp.passport = null;
      insp.history = [];
      renderInspector();
    }
    setInspOpen(false);
  }
  /* close the inspector back to its strip (narrow widths) and hand focus back to the figure, or to the strip when it was opened empty */
  function closeInspector() {
    if (insp.selected) insp.selected.classList.remove('is-selected');
    insp.desc = null;
    insp.passport = null;
    insp.history = [];
    renderInspector();
    setInspOpen(false);
    const r = shell.returnEl;
    if (r && document.contains(r)) r.focus();
    else shell.canvas.focus();
  }
  function openInspectorEmpty() {
    setInspOpen(true);
    renderInspector();
    // the strip is rebuilt with the pane: it is where focus returns when the empty inspector is closed
    shell.returnEl = WB.qs('.insp-open', shell.insp);
    const h = WB.qs('.insp-empty', shell.insp);
    if (h) h.focus({ preventScroll: true });
  }
  /* WB.inspect(desc, originEl): the public entry. desc is a passport descriptor; chart agents pass { t: 'chart', chartId }. */
  WB.inspect = function (desc, originEl, opts) {
    const o = opts || {};
    const from = originEl || document.activeElement;
    const inInspector = from && shell.insp.contains(from);
    if (!inInspector) {
      shell.returnEl = from;
      insp.history = [];
      if (insp.selected) insp.selected.classList.remove('is-selected');
      insp.selected = from && from.classList ? from : null;
      if (insp.selected) insp.selected.classList.add('is-selected');
    } else if (insp.desc) insp.history.push(insp.desc);
    insp.desc = desc;
    insp.passport = WB.buildPassport(desc);
    if (o.tab) insp.tab = o.tab;
    else if (insp.tab === 'gaps' && !inInspector) insp.tab = 'source';
    setInspOpen(true);
    renderInspector();
    if (!o.noFocus) {
      const h = WB.qs('.pp-title', shell.insp) || WB.qs('.insp-empty', shell.insp);
      if (h) h.focus({ preventScroll: true });
    }
    WB.announce('Passport opened: ' + insp.passport.title);
  };
  function ppField(label, value, mono) {
    return [el('dt', null, label), el('dd', { class: mono ? 'num wrap' : '' }, value)];
  }
  function chipButton(desc, id, label, synthetic) {
    // an input's id: a code (C12, total_debt) prints mono; a label (Current value) prints as text
    const code = /^[A-Za-z]{0,3}\d+$|^[a-z0-9_:.@-]+$|^[A-Z0-9_:.@-]+$/.test(String(id));
    const b = el('button', { type: 'button', class: 'pchip', 'data-pdesc': '1' }, [synthetic ? WB.mark('synthetic') : id && /^C\d+/.test(id) ? WB.mark('cited') : WB.mark('calculated'), el('span', { class: 'pc-id' + (code ? ' num' : ' pc-id-t') }, id), el('span', { class: 'pc-l' }, label)]);
    b.addEventListener('click', () => WB.inspect(desc, b));
    return b;
  }
  /* a short code (C12, G8, CP-6) heads the passport; a long id (a table, Model line or chart id) is a quiet line at its foot */
  const shortCode = (c) => !!c && c.length <= 10 && !/[._:@]/.test(c);
  function renderPassportEl(p, opts) {
    const o = opts || {};
    const kindWord = WB.originWord[p.kind] || 'No source stated';
    const root = el('div', { class: 'pp pp-' + p.kind });
    const head = shortCode(p.code) ? p.code : '';
    const foot = [p.code && !head ? p.code : '', p.id || ''].filter(Boolean).join(' · ');
    root.appendChild(el('div', { class: 'pp-top' }, [WB.mark(p.kind, { size: 12 }), head ? el('span', { class: 'pp-code num' }, head) : null, el('span', { class: 'pp-kind' }, kindWord.toUpperCase()), p.sub ? el('span', { class: 'pp-sub' }, p.sub) : null]));
    root.appendChild(el(o.static ? 'h4' : 'h3', { class: 'pp-title', tabindex: o.static ? false : '-1' }, p.title));
    if (!o.static && insp.history.length) {
      const back = el('button', { type: 'button', class: 'pp-back' }, [WB.icon('arrow-left', { size: 12, stroke: 1.8 }), 'Back']);
      back.addEventListener('click', () => {
        const prev = insp.history.pop();
        insp.desc = prev;
        insp.passport = WB.buildPassport(prev);
        renderInspector();
        const h = WB.qs('.pp-title', shell.insp);
        if (h) h.focus({ preventScroll: true });
      });
      root.appendChild(back);
    }
    const dl = el('dl', { class: 'pp-f' });
    p.fields.forEach(([l, v, m]) => v !== '' && v != null && dl.append(...ppField(l, v, m)));
    if (p.formula) dl.append(el('dt', null, 'Formula'), el('dd', null, el('code', { class: 'pp-formula' }, p.formula)));
    root.appendChild(dl);
    if (p.inputs.length) {
      root.appendChild(el('h4', { class: 'pp-h' }, 'Inputs'));
      root.appendChild(el('div', { class: 'pp-chips' }, p.inputs.map((i) => chipButton(i.desc, i.id, i.label, i.desc && i.desc.t === 'cite' && WB.citation(i.desc.module, i.desc.id) && WB.citation(i.desc.module, i.desc.id).synthetic))));
    }
    if (p.excerpt) {
      root.appendChild(el('h4', { class: 'pp-h' }, p.kind === 'synthetic' ? 'TEST DATA rationale' : 'Verbatim excerpt'));
      root.appendChild(el('pre', { class: 'pp-ex' }, p.excerpt));
    }
    if (p.cites.length && !p.inputs.length) {
      root.appendChild(el('h4', { class: 'pp-h' }, 'Cites (' + p.cites.length + ')'));
      root.appendChild(el('div', { class: 'pp-chips' }, p.cites.map((c) => chipButton(c.desc, c.id, c.label, c.synthetic))));
    }
    if (p.usedIn != null || p.evidenceAnchor) {
      const bits = [];
      if (p.evidenceAnchor) bits.push(el('a', { href: WB.href('evidence', p.evidenceAnchor) }, 'Open in Evidence'));
      if (p.usedIn != null) bits.push(el('span', null, 'Used in ' + p.usedIn + (p.usedIn === 1 ? ' place' : ' places')));
      root.appendChild(el('p', { class: 'pp-use' }, bits.flatMap((b, i) => (i ? [' · ', b] : [b]))));
      if (p.usedPlaces && p.usedPlaces.length) {
        root.appendChild(
          el('ul', { class: 'pp-places' }, p.usedPlaces.slice(0, 8).map((u) => {
            const href = u.kind === 'analysis' ? WB.href('module/' + u.module + '/p-analysis') : u.kind === 'table' ? (u.module === 'RUN_BRIEF' ? WB.href('front') : WB.href('module/' + u.module + '/t-' + WB.cssId(u.table))) : WB.href('module/MODEL');
            const label = u.kind === 'analysis' ? WB.moduleName(u.module) + ', analysis' : u.kind === 'table' ? WB.tableTitle(u.table) + ', row ' + (u.row + 1) : 'Model, ' + u.line;
            return el('li', null, el('a', { href }, label));
          }))
        );
      }
    }
    if (p.note) root.appendChild(el('p', { class: 'pp-note' }, p.note));
    if (p.gaps.length && p.kind !== 'gap') {
      root.appendChild(el('h4', { class: 'pp-h' }, 'Gap'));
      root.appendChild(gapList(p.gaps.slice(0, 3)));
    }
    if (p.kind === 'gap' && p.gaps.length > 1) {
      root.appendChild(el('h4', { class: 'pp-h' }, 'Gaps in this module'));
      root.appendChild(gapList(p.gaps));
    }
    // the raw id in whole tokens (table, row, column): each wraps only at its own separators, so nothing is cut mid-word
    if (foot) {
      const tok = (t) => el('span', { class: 'pp-tok' }, t.split(/([/#:@._-])/).flatMap((part, i) => (i % 2 ? [part, el('wbr')] : [part])));
      root.appendChild(el('p', { class: 'pp-id num', title: 'Raw id in the run file' }, foot.split(' \u00B7 ').map(tok)));
    }
    return root;
  }
  WB.renderPassport = (p) => renderPassportEl(p, { static: true });
  function gapList(items) {
    return el('ul', { class: 'pp-gaps' }, items.map((g) => el('li', null, [el('span', { class: 'pg-ids num' }, g.ids.join(' ') || 'gap'), el('span', { class: 'pg-t' }, [el('strong', null, g.missing + '. '), g.text.slice(g.missing.length).replace(/^[\s:.]+/, '')])])));
  }
  function renderTableTab(p) {
    if (p.table) {
      const t = WB.table(p.table.id);
      if (!t) return el('p', { class: 'insp-empty' }, 'Table ' + p.table.id + ' is not in this run.');
      const w = WB.renderTable(t, { maxRows: Math.max(40, p.table.row + 10), caption: WB.tableTitle(t.id) });
      const tr = WB.qs('tr[data-r="' + p.table.row + '"]', w);
      if (tr) {
        tr.classList.add('hl');
        requestAnimationFrame(() => tr.scrollIntoView({ block: 'center' }));
      }
      return el('div', { class: 'ti' }, [el('p', { class: 'ti-h' }, [el('strong', null, WB.tableTitle(t.id)), el('span', { class: 'num muted' }, ' ' + t.id)]), w]);
    }
    if (p.chart) {
      const ch = (WB.run.charts || []).find((c) => c.chart_id === p.chart);
      if (ch) return el('div', { class: 'ti' }, [el('p', { class: 'ti-h' }, [el('strong', null, WB.chartTitle(ch.chart_id)), null]), WB.chartTwinTables(ch).map((t) => WB.renderTable(t, { maxRows: 25, caption: WB.tableTitle(t.id) }))]);
    }
    return el('p', { class: 'insp-empty' }, 'No table for this figure. Select a table figure or a chart mark to see its table here.');
  }
  function renderGapsTab() {
    const mods = (WB.page.gapModules || []).slice();
    const out = el('div', { class: 'gt' });
    let n = 0;
    mods.forEach((m) => {
      const items = WB.gapItems(m);
      if (!items.length) return;
      out.appendChild(el('h4', { class: 'pp-h' }, WB.moduleName(m) + ' · ' + m));
      out.appendChild(gapList(items));
      n += items.length;
    });
    if (!n) out.appendChild(el('p', { class: 'insp-empty' }, 'No gaps recorded for this page.'));
    return out;
  }
  function renderInspector() {
    const root = shell.insp;
    const tabs = [
      ['source', 'Source'],
      ['table', 'Table'],
      ['gaps', 'Gaps'],
    ];
    const bar = el('div', { class: 'insp-tabs', role: 'tablist', 'aria-label': 'Inspector tabs' }, tabs.map(([k, l]) => {
      const b = el('button', { type: 'button', role: 'tab', id: 'it-' + k, class: 'itab' + (insp.tab === k ? ' on' : ''), 'aria-selected': insp.tab === k ? 'true' : 'false', 'aria-controls': 'insp-panel', tabindex: insp.tab === k ? '0' : '-1' }, l);
      b.addEventListener('click', () => {
        insp.tab = k;
        renderInspector();
        const t = document.getElementById('it-' + k);
        if (t) t.focus();
      });
      b.addEventListener('keydown', (e) => {
        if (e.key !== 'ArrowRight' && e.key !== 'ArrowLeft') return;
        const i = tabs.findIndex((x) => x[0] === insp.tab) + (e.key === 'ArrowRight' ? 1 : -1);
        const nk = tabs[(i + tabs.length) % tabs.length][0];
        insp.tab = nk;
        renderInspector();
        document.getElementById('it-' + nk).focus();
      });
      return b;
    }));
    let body;
    if (insp.tab === 'gaps') body = renderGapsTab();
    else if (!insp.passport) body = el('div', { class: 'insp-empty', tabindex: '-1' }, [el('strong', null, 'Select a figure'), el('p', null, 'Cited, calculated, synthetic, model-written and illustrative figures each open a passport here. Select a chart mark or a chip, or press ? for the key.')]);
    else if (insp.tab === 'table') body = renderTableTab(insp.passport);
    else body = renderPassportEl(insp.passport);
    const strip = el('button', { type: 'button', class: 'insp-open', 'aria-label': 'Open the inspector', title: 'Open the inspector' }, [WB.icon('chevron-left', { size: 14, stroke: 1.8 }), el('span', { class: 'io-l' }, 'Inspector')]);
    strip.addEventListener('click', openInspectorEmpty);
    const close = el('button', { type: 'button', class: 'btn-x insp-close', 'aria-label': 'Close the inspector', title: 'Close the inspector' }, WB.icon('close', { size: 14, stroke: 1.8 }));
    close.addEventListener('click', closeInspector);
    root.replaceChildren(
      strip,
      el('header', { class: 'insp-h' }, [el('h2', null, 'Inspector'), bar, close]),
      el('div', { class: 'insp-body', id: 'insp-panel', role: 'tabpanel', 'aria-labelledby': 'it-' + insp.tab }, body),
      el('footer', { class: 'insp-f' }, [el('strong', null, 'Keys'), ' ', el('span', { class: 'num' }, '←↑→↓'), ' figures · ', el('span', { class: 'num' }, 'Enter'), ' passport · ', el('span', { class: 'num' }, 'Esc'), ' back'])
    );
  }

  /* ---------- print: passports as numbered endnotes ---------- */
  let printState = null;
  function beforePrint() {
    const canvas = shell.canvas;
    printState = { panels: [], notes: null };
    WB.qsa('.panel.is-collapsed', canvas).forEach((p) => {
      printState.panels.push(p);
      p._setOpen(true);
    });
    WB.qsa('.tw', canvas).forEach((w) => w._expand && w._expand());
    // disclosures print open: the extra call lines and the Sources lists
    printState.details = WB.qsa('details:not([open])', canvas);
    printState.details.forEach((d) => (d.open = true));
    const notes = [];
    const index = new Map();
    const add = (key, make) => {
      if (!index.has(key)) {
        notes.push(make());
        index.set(key, notes.length);
      }
      return index.get(key);
    };
    WB.qsa('[data-ref]', canvas).forEach((node) => {
      const d = WB.getRef(node.dataset.ref);
      if (!d) return;
      const p = WB.buildPassport(d);
      const nums = [];
      for (const c of p.cites) {
        if (c.missing) continue;
        nums.push(add('cite:' + c.module + ':' + c.id, () => ({ code: c.id, text: c.label, excerpt: (WB.citation(c.module, c.id) || {}).excerpt, kind: c.synthetic ? 'synthetic' : 'cited' })));
      }
      if (d.t === 'cite' && p.kind !== 'none') nums.push(add('cite:' + d.module + ':' + d.id, () => ({ code: p.code, text: p.title + ' · ' + (p.fields[1] ? p.fields[1][1] : ''), excerpt: p.excerpt, kind: p.kind })));
      if (p.formula) nums.push(add('calc:' + p.formula, () => ({ code: 'calc', text: p.formula, kind: 'calculated' })));
      if (p.kind === 'gap' && p.gaps[0]) nums.push(add('gap:' + p.gaps[0].text, () => ({ code: p.gaps[0].ids.join(' ') || 'gap', text: p.gaps[0].text, kind: 'gap' })));
      if (nums.length) node.dataset.endnote = endnoteMark(Array.from(new Set(nums)).sort((a, b) => a - b));
    });
    if (notes.length) {
      const sec = el('section', { class: 'endnotes', id: 'endnotes', 'aria-label': 'Endnotes' }, [
        el('h2', null, 'Endnotes: passports of the figures on this page'),
        el('ol', null, notes.map((n) => el('li', null, [el('span', { class: 'en-c num' }, n.code), ' ', el('span', { class: 'en-k' }, (WB.originWord[n.kind] || '') + '. '), el('span', { class: 'en-t' }, n.text), n.excerpt ? el('span', { class: 'en-x' }, ' “' + n.excerpt + '”') : null]))),
      ]);
      canvas.appendChild(sec);
      printState.notes = sec;
    }
  }
  /* [7], [7–9] for a consecutive run, [7,12+] when there are more */
  function endnoteMark(nums) {
    if (nums.length === 1) return String(nums[0]);
    const run = nums.every((n, i) => i === 0 || n === nums[i - 1] + 1);
    if (run) return nums[0] + '\u2013' + nums[nums.length - 1];
    return nums.slice(0, 2).join(',') + (nums.length > 2 ? '+' : '');
  }
  function afterPrint() {
    if (!printState) return;
    printState.panels.forEach((p) => p._setOpen(false));
    (printState.details || []).forEach((d) => (d.open = false));
    if (printState.notes) printState.notes.remove();
    WB.qsa('[data-endnote]', shell.canvas).forEach((n) => delete n.dataset.endnote);
    printState = null;
  }
  WB.beforePrint = beforePrint;
  WB.afterPrint = afterPrint;

  /* ---------- start ---------- */
  function typing(t) {
    return t && (t.tagName === 'INPUT' || t.tagName === 'TEXTAREA' || t.tagName === 'SELECT' || t.isContentEditable);
  }
  WB.start = function () {
    const root = el('div', { id: 'app', 'data-nav': window.matchMedia('(min-width: 1360px)').matches ? 'open' : 'closed', 'data-insp': 'closed' });
    shell.root = root;
    shell.rail = el('nav', { class: 'rail on-navy', 'aria-label': 'Destinations' });
    shell.nav = el('aside', { class: 'navigator', id: 'navigator', 'aria-label': 'Navigator' });
    shell.canvas = el('main', { class: 'canvas', id: 'canvas', tabindex: '-1', 'aria-label': 'Report' });
    shell.insp = el('aside', { class: 'inspector', id: 'inspector', 'aria-label': 'Inspector' });
    shell.layers = el('div', { id: 'layers' });
    shell.live = el('div', { id: 'live', class: 'sr-only', 'aria-live': 'polite', role: 'status' });
    root.append(el('a', { class: 'skip', href: '#canvas', onclick: (e) => { e.preventDefault(); shell.canvas.focus(); } }, 'Skip to the report'), shell.rail, shell.nav, shell.canvas, shell.insp, shell.layers, shell.live);
    document.body.appendChild(root);
    renderInspector();

    document.addEventListener('click', (e) => {
      const t = e.target.closest && e.target.closest('[data-ref]');
      if (!t) return;
      if (t.dataset.pdesc) return;
      const d = WB.getRef(t.dataset.ref);
      if (d) WB.inspect(d, t);
    });
    shell.canvas.addEventListener('scroll', updateSpy, { passive: true });
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape') {
        if (shell.layer) {
          e.preventDefault();
          closeLayer();
          return;
        }
        if (shell.insp.contains(document.activeElement)) {
          if (narrow() && shell.root.dataset.insp === 'closed') return;
          e.preventDefault();
          // narrow: Esc also closes the inspector back to its strip; wide: it only hands focus back and the passport stays
          if (narrow()) {
            closeInspector();
            return;
          }
          const r = shell.returnEl;
          if (r && document.contains(r)) r.focus();
          else shell.canvas.focus();
        }
        return;
      }
      // chart marks and other non-native controls that carry a passport: Enter and Space open it
      if ((e.key === 'Enter' || e.key === ' ') && e.target.closest && !/^(BUTTON|A|INPUT|SELECT|TEXTAREA|SUMMARY)$/.test(e.target.tagName)) {
        const ref = e.target.closest('[data-ref]');
        if (ref && ref === e.target) {
          e.preventDefault();
          ref.dispatchEvent(new MouseEvent('click', { bubbles: true, cancelable: true }));
          return;
        }
      }
      if (typing(e.target) || e.ctrlKey || e.metaKey || e.altKey) return;
      if (e.key === '/') {
        e.preventDefault();
        openSearch();
      } else if (e.key === '?') {
        e.preventDefault();
        openHelp();
      }
    });
    window.addEventListener('hashchange', () => route(false));
    window.addEventListener('beforeprint', beforePrint);
    window.addEventListener('afterprint', afterPrint);
    route(true);
  };

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', WB.start);
  else WB.start();
})();
