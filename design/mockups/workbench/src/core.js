/* WB core: error capture, run registry, data helpers, provenance, formatting, DOM helper, icon set.
   Nothing here touches the document layout; shell.js and render.js build on it. */
(function () {
  'use strict';
  const WB = (window.WB = window.WB || {});

  /* ---------- error capture: records, never swallows ---------- */
  const errors = (window.__wbErrors = window.__wbErrors || []);
  document.documentElement.dataset.errors = String(errors.length);
  WB.recordError = function (kind, err, where) {
    const e = err instanceof Error ? err : null;
    errors.push({
      kind,
      message: e ? e.message : String(err),
      stack: e ? String(e.stack || '') : '',
      where: where || '',
      at: Date.now(),
    });
    document.documentElement.dataset.errors = String(errors.length);
    if (errors.length === 1) {
      document.documentElement.dataset.errorFirst = (kind + ': ' + errors[0].message + ' ' + errors[0].where).slice(0, 300);
      document.documentElement.dataset.errorStack = errors[0].stack.replace(/https?:\/\/[^\s)]*\/rbot-workbench\.html/g, 'wb').slice(0, 700);
    }
  };
  window.addEventListener('error', (ev) => {
    WB.recordError('error', ev.error || ev.message, (ev.filename || '') + ':' + (ev.lineno || 0));
  });
  window.addEventListener('unhandledrejection', (ev) => {
    WB.recordError('unhandledrejection', ev.reason);
  });

  /* ---------- DOM helper (data never becomes markup) ---------- */
  const SVG_NS = 'http://www.w3.org/2000/svg';
  function applyAttrs(node, attrs) {
    if (!attrs) return;
    for (const k of Object.keys(attrs)) {
      const v = attrs[k];
      if (v === false || v == null) continue;
      if (k === 'class' || k === 'className') node.setAttribute('class', v);
      else if (k === 'text') node.textContent = v;
      else if (k === 'html') throw new Error('WB.el: html is not allowed; build the DOM with el()');
      else if (k === 'style' && typeof v === 'object') Object.assign(node.style, v);
      else if (k === 'dataset') Object.assign(node.dataset, v);
      else if (k.slice(0, 2) === 'on' && typeof v === 'function') node.addEventListener(k.slice(2), v);
      else node.setAttribute(k, v === true ? '' : String(v));
    }
  }
  function appendChildren(node, children) {
    if (children == null || children === false) return;
    if (Array.isArray(children)) {
      for (const c of children) appendChildren(node, c);
    } else if (children instanceof Node) {
      node.appendChild(children);
    } else {
      node.appendChild(document.createTextNode(String(children)));
    }
  }
  WB.el = function (tag, attrs, children) {
    const node = document.createElement(tag);
    applyAttrs(node, attrs);
    appendChildren(node, children);
    return node;
  };
  WB.svg = function (tag, attrs, children) {
    const node = document.createElementNS(SVG_NS, tag);
    applyAttrs(node, attrs);
    appendChildren(node, children);
    return node;
  };
  WB.frag = function (children) {
    const f = document.createDocumentFragment();
    appendChildren(f, children);
    return f;
  };
  WB.text = (s) => document.createTextNode(s == null ? '' : String(s));
  WB.qs = (sel, root) => (root || document).querySelector(sel);
  WB.qsa = (sel, root) => Array.from((root || document).querySelectorAll(sel));
  WB.cssId = (s) => String(s).replace(/[^A-Za-z0-9_-]+/g, '-');

  /* ---------- icon set: one family, 16px, 1.5px stroke ---------- */
  const P = (d, extra) => ['path', Object.assign({ d }, extra || {})];
  const C = (cx, cy, r, extra) => ['circle', Object.assign({ cx, cy, r }, extra || {})];
  const DOC = 'M4 2.5h5.5L12 5v8.5H4z';
  const ICONS = {
    frontpage: [P('M2.5 3h11v10h-11z'), P('M2.5 6.5h11'), P('M6.5 6.5V13')],
    analysis: [P('M2 12l3.5-4 3 2.5L14 4'), P('M10.5 4H14v3.5')],
    model: [P('M2.5 2.5h11v11h-11z'), P('M2.5 6.2h11'), P('M2.5 9.8h11'), P('M6.2 2.5v11'), P('M9.8 2.5v11')],
    fit: [P('M8 2.5a5.5 5.5 0 1 0 5.5 5.5H8z'), P('M9.5 1.8a4.7 4.7 0 0 1 4.7 4.7H9.5z')],
    evidence: [P(DOC), P('M9.5 2.5V5H12'), P('M6 8h4'), P('M6 10.5h4')],
    limitations: [P('M8 2.2l6.2 11H1.8z'), P('M8 6.5v3'), P('M8 11.5v.4')],
    system: [P('M8 2l6 3.2-6 3.2-6-3.2z'), P('M2 8.2l6 3.2 6-3.2'), P('M2 11l6 3.2 6-3.2')],
    search: [C(7, 7, 4.5), P('M10.5 10.5L14 14')],
    help: [C(8, 8, 6.5), P('M6 6.5a2 2 0 1 1 3 1.7c-.7.4-1 .8-1 1.5'), P('M8 12v.5')],
    print: [P('M4 6V2h8v4'), P('M4 12H2V6h12v6h-2'), P('M4 10h8v4H4z')],
    sidebar: [P('M2.5 3h11v10h-11z'), P('M6.5 3v10')],
    'chevron-down': [P('M4 6l4 4 4-4')],
    'chevron-up': [P('M4 10l4-4 4 4')],
    'chevron-right': [P('M6 4l4 4-4 4')],
    'chevron-left': [P('M10 4L6 8l4 4')],
    'arrow-right': [P('M3 8h10'), P('M9 4l4 4-4 4')],
    'arrow-left': [P('M13 8H3'), P('M7 4L3 8l4 4')],
    'arrow-in': [P('M3 8h9'), P('M8.5 4.5L12 8l-3.5 3.5'), P('M13.5 3v10')],
    close: [P('M4 4l8 8'), P('M12 4l-8 8')],
    cross: [P('M4 4l8 8'), P('M12 4l-8 8')],
    link: [P('M6.5 9.5l3-3'), P('M7 4.5l1-1a2.5 2.5 0 0 1 3.5 3.5l-1 1'), P('M9 11.5l-1 1A2.5 2.5 0 0 1 4.5 9l1-1')],
    copy: [P('M5.5 5.5h7v8h-7z'), P('M3.5 10.5v-8h7')],
    tick: [P('M3 8.5l3.2 3.2L13 4.8')],
    'status-pass': [C(8, 8, 6.5), P('M5 8l2 2 4-4')],
    'status-limited': [C(8, 8, 6.5), ['path', { d: 'M8 1.5A6.5 6.5 0 0 1 8 14.5Z', fill: 'currentColor' }]],
    'status-blocked': [C(8, 8, 6.5), P('M3.4 12.6l9.2-9.2')],
    'status-notrun': [C(8, 8, 6.5, { 'stroke-dasharray': '2 2' }), P('M5.5 8h5')],
    warn: [P('M8 2.2l6.2 11H1.8z'), P('M8 6.5v3'), P('M8 11.5v.4')],
    'arrow-up': [P('M8 13V3'), P('M4 7l4-4 4 4')],
    'arrow-down': [P('M8 3v10'), P('M4 9l4 4 4-4')],
    'arrow-flat': [P('M3 8h10'), P('M10 5l3 3-3 3')],
    plus: [P('M8 3v10'), P('M3 8h10')],
    minus: [P('M3 8h10')],
    emptyset: [C(8, 8, 4.8), P('M4.6 11.4l6.8-6.8')],
    table: [P('M2.5 3.5h11v9h-11z'), P('M2.5 7h11'), P('M7 3.5v9')],
    chart: [P('M2.5 13.5h11'), P('M4.5 13V8'), P('M8 13V4'), P('M11.5 13V6.5')],
    'doc-stack': [P('M5.5 2.5H12v8.5'), P('M3.5 4.5H10v9H3.5z'), P('M5.5 8H8'), P('M5.5 10.5H8')],
    lock: [P('M4.5 7h7v6.5h-7z'), P('M6 7V5a2 2 0 0 1 4 0v2')],
    tag: [P('M2.5 8.2V2.5h5.7l5.3 5.3-5.7 5.7z'), P('M5.6 5.6v.1')],
    clock: [C(8, 8, 6), P('M8 4.5V8l2.5 1.5')],
    gauge: [P('M2.5 11.5a5.5 5.5 0 0 1 11 0'), P('M8 11.5L10.5 7'), P('M3 11.5h10')],
    info: [C(8, 8, 6.5), P('M8 7v4.5'), P('M8 4.7v.1')],
    bank: [P('M2 6.5L8 3l6 3.5'), P('M3.5 7v5'), P('M6.5 7v5'), P('M9.5 7v5'), P('M12.5 7v5'), P('M2.5 13h11')],
    calendar: [P('M2.5 3.5h11v10h-11z'), P('M2.5 6.5h11'), P('M5 2v3'), P('M11 2v3')],
    drop: [P('M8 2.2c2.4 3 4 4.8 4 7a4 4 0 0 1-8 0c0-2.2 1.6-4 4-7z')],
    scales: [P('M8 2.5v11'), P('M3 4.5h10'), P('M3 4.5L1.5 9h3z'), P('M13 4.5L11.5 9h3z'), P('M5.5 13.5h5')],
    recovery: [P('M13 8a5 5 0 1 1-1.8-3.8'), P('M13 2.5v3h-3')],
    business: [P('M3.5 13.5v-10h6v10'), P('M9.5 6.5h3v7'), P('M5.5 5.5h2'), P('M5.5 8h2'), P('M5.5 10.5h2'), P('M2 13.5h12')],
    'doc-filing': [P(DOC), P('M9.5 2.5V5H12'), P('M6 8h4'), P('M6 10.5h4')],
    'doc-legal': [P(DOC), P('M9.5 2.5V5H12'), C(8, 9.2, 1.7), P('M7.2 10.7L6.6 12.5l1.4-.6 1.4.6-.6-1.8')],
    'doc-earnings': [P(DOC), P('M9.5 2.5V5H12'), P('M6 11.5V9'), P('M8 11.5V7.5'), P('M10 11.5V9.5')],
    'doc-market': [P(DOC), P('M9.5 2.5V5H12'), P('M5.8 11l1.7-2 1.2 1 1.5-2.2')],
    'doc-portfolio': [P(DOC), P('M9.5 2.5V5H12'), P('M8 7.5a2.3 2.3 0 1 0 2.3 2.3H8z')],
    'doc-web': [C(8, 8, 6), P('M2 8h12'), P('M8 2c2 2 2 10 0 12'), P('M8 2c-2 2-2 10 0 12')],
    pen: [P('M3 13l1-4 7-7 3 3-7 7z')],
    flask: [P('M6.5 2.5h3'), P('M7 2.5v4L3.5 12.5a1 1 0 0 0 .9 1.5h7.2a1 1 0 0 0 .9-1.5L9 6.5v-4')],
    'dashed-square': [['rect', { x: 3, y: 3, width: 10, height: 10, 'stroke-dasharray': '2.4 2' }]],
    function: [P('M5 3h6'), P('M5 13h6'), P('M9.2 3L6.8 13')],
    'collapse-all': [P('M4 6l4-3 4 3'), P('M4 10l4 3 4-3')],
    'expand-all': [P('M4 3l4 3 4-3'), P('M4 13l4-3 4 3')],
    filter: [P('M2.5 3.5h11L9.5 8.5v4l-3 1v-5z')],
    sparkle: [P('M8 2.5l1.3 3.7 3.7 1.3-3.7 1.3L8 12.5 6.7 8.8 3 7.5l3.7-1.3z')],
  };
  WB.iconNames = Object.keys(ICONS);
  WB.icon = function (name, opts) {
    const o = opts || {};
    const def = ICONS[name];
    if (!def) throw new Error('WB.icon: unknown icon "' + name + '"');
    const size = o.size || 16;
    const attrs = {
      width: size,
      height: size,
      viewBox: '0 0 16 16',
      fill: 'none',
      stroke: 'currentColor',
      'stroke-width': o.stroke || 1.5,
      'stroke-linecap': 'round',
      'stroke-linejoin': 'round',
      class: 'ic' + (o.cls ? ' ' + o.cls : ''),
    };
    if (o.label) {
      attrs.role = 'img';
      attrs['aria-label'] = o.label;
    } else attrs['aria-hidden'] = 'true';
    const svg = WB.svg('svg', attrs);
    if (o.label) svg.appendChild(WB.svg('title', null, o.label));
    for (const [tag, a] of def) svg.appendChild(WB.svg(tag, a));
    return svg;
  };

  /* Provenance marks: shape carries the meaning, never colour alone. 10px, quiet by default. */
  const MARKS = {
    cited: [['path', { d: 'M1.5 .75h4.2L8.5 3.6v5.65h-7z' }], ['path', { d: 'M5.6 .8v2.9h2.9' }]],
    calculated: [['rect', { x: 0.75, y: 0.75, width: 8.5, height: 8.5, fill: 'currentColor', stroke: 'none' }], ['path', { d: 'M2.6 3.9h4.8M2.6 6.1h4.8', stroke: '#fff', 'stroke-width': 1 }]],
    synthetic: [['path', { d: 'M3.9 1h2.2M4.2 1v3L1.8 8.4a.7.7 0 0 0 .6 1h5.2a.7.7 0 0 0 .6-1L5.8 4V1' }]],
    model: [['path', { d: 'M1.5 8.5l.6-2.4 4.6-4.6 1.8 1.8-4.6 4.6z' }]],
    gap: [['circle', { cx: 5, cy: 5, r: 3.3 }], ['path', { d: 'M2.7 7.3l4.6-4.6' }]],
    illustrative: [['rect', { x: 1, y: 1, width: 8, height: 8, 'stroke-dasharray': '2 1.5' }]],
    // no source stated: a ring holding a question mark (the gap mark is a slashed ring, the illustrative mark a dashed square)
    none: [['circle', { cx: 5, cy: 5, r: 4.1 }], ['path', { d: 'M3.9 4.1a1.2 1.2 0 1 1 1.7 1.1c-.4.2-.6.4-.6.9', 'stroke-linecap': 'round' }], ['path', { d: 'M5 7.7h.01', 'stroke-linecap': 'round' }]],
  };
  WB.originWord = {
    cited: 'Cited',
    calculated: 'Calculated',
    synthetic: 'Synthetic',
    model: 'Model-written',
    gap: 'n/a',
    illustrative: 'Illustrative',
    none: 'No source stated',
    plain: '',
  };
  WB.mark = function (kind, opts) {
    const def = MARKS[kind];
    if (!def) return null;
    const o = opts || {};
    const size = o.size || 10;
    const svg = WB.svg('svg', {
      width: size,
      height: size,
      viewBox: '0 0 10 10',
      fill: 'none',
      stroke: 'currentColor',
      'stroke-width': 1,
      'stroke-linejoin': 'round',
      class: 'mk mk-' + kind,
      'aria-hidden': 'true',
    });
    for (const [tag, a] of def) svg.appendChild(WB.svg(tag, a));
    return svg;
  };

  /* ---------- view registry (so later agents add Model, Fit, Design system, Front Pages) ---------- */
  WB.views = {};
  WB.registerView = function (name, def) {
    if (!def || typeof def.render !== 'function') throw new Error('registerView(' + name + '): render is required');
    WB.views[name] = def;
  };
  WB.frontPages = {};
  WB.registerFrontPage = function (frontPageId, fn) {
    WB.frontPages[frontPageId] = fn;
  };

  /* ---------- module metadata ---------- */
  const modulesEl = document.getElementById('rbot-modules');
  WB.modules = modulesEl ? JSON.parse(modulesEl.textContent) : {};
  const FALLBACK_NAMES = {
    'CP-DR': 'Deep research',
    'CP-8': 'What changed',
    'CP-L10': 'Quick screen',
    MODEL: 'Financial model',
    PROJECTION: 'Projection',
    FIT: 'Portfolio Fit',
    RUN_BRIEF: 'Run Brief',
    'CP-2E': 'Macro and hedging',
  };
  WB.moduleName = (id) => (WB.modules[id] && WB.modules[id].name) || FALLBACK_NAMES[id] || id;
  WB.moduleQuestion = (id) => (WB.modules[id] && WB.modules[id].question) || '';

  WB.PATHWAYS = {
    FULL_CREDIT_ASSESSMENT: 'Full Credit Assessment',
    EARNINGS_UPDATE: 'Earnings Update',
    RELATIVE_VALUE: 'Relative Value',
    COVENANT_REFINANCING: 'Covenant & Refinancing',
    DISTRESSED_RESTRUCTURING: 'Distressed & Restructuring',
    PORTFOLIO_DECISION: 'Portfolio Decision',
  };
  WB.FRONT_PAGES = {
    credit_snapshot: 'Credit Snapshot',
    earnings_update: 'Earnings Update',
    relative_value: 'Relative Value',
    covenant_refinancing: 'Covenant & Refinancing',
    distressed_restructuring: 'Distressed & Restructuring',
    portfolio_decision: 'Portfolio Decision',
  };
  WB.CHART_TITLES = {
    'chart.model_strip': 'Model chart strip',
    'chart.maturity_wall': 'Maturity wall',
    'chart.capital_structure': 'Debt stack by rank',
    'chart.ebitda_bridge': 'EBITDA bridge',
    'chart.adjusted_debt_bridge': 'Adjusted debt bridge',
    'chart.headline_results': 'Headline results',
    'chart.kpi_changes': 'KPI changes',
    'chart.peer_ranges': 'Peer ranges',
    'chart.implied_ev': 'Implied EV by method',
    'chart.liquidity_sources': 'Liquidity by accessibility',
    'chart.cash_uses': 'Cash uses by timing',
    'chart.liquidity_bridge': 'Liquidity bridge, 12 months',
    'chart.rate_fx_tornado': 'Rate and FX sensitivities',
    'chart.downside_tornado': 'Downside sensitivities',
    'chart.risk_matrix': 'Probability and impact',
    'chart.forecast_lines': 'Forecast cases',
    'chart.credit_path': 'Credit path',
    'chart.rating_triggers': 'Rating triggers',
    'chart.rv_loan': 'Loan relative value',
    'chart.rv_hy': 'High-yield relative value',
    'chart.talk_range': 'Talk valuation range',
    'chart.factor_scores': 'Protection score by area',
    'chart.spread_curve': 'Spread against maturity',
    'chart.implied_pd': 'Market-implied default probability',
    'chart.lme_exposure': 'Exposure by case',
    'chart.funding_gap': 'Funding gap',
    'chart.covenant_headroom': 'Covenant headroom',
    'chart.basket_capacity': 'Baskets used and remaining',
    'chart.value_allocation': 'Value allocation',
    'chart.recovery_by_class': 'Recovery by class',
    'chart.issue_counts': 'Issues by module and severity',
    'chart.topic_counts': 'Topics by materiality',
    'chart.expected_realised': 'Expected against realised',
    'chart.what_changed': 'What changed',
    'chart.fit_bullets': 'Limit headroom',
  };
  WB.chartTitle = (id) => WB.CHART_TITLES[id] || String(id).replace(/^chart\./, '').replace(/_/g, ' ');
  WB.REASONS = {
    NOT_SOURCED: 'Not in the sources',
    NOT_APPLICABLE: 'Not applicable to this line or period',
    COMPONENT_MISSING: 'A component of the calculation is missing',
    NOT_PROJECTED: 'Not projected',
  };

  /* ---------- run registry ---------- */
  const runScripts = WB.qsa('script.rbot-run');
  WB.runIds = runScripts.map((s) => s.dataset.run);
  const runText = {};
  runScripts.forEach((s) => (runText[s.dataset.run] = s));
  const runCache = {};
  WB.run = null;

  WB.loadRun = function (id) {
    if (runCache[id]) return runCache[id];
    const node = runText[id];
    if (!node) return null;
    const r = JSON.parse(node.textContent);
    r._id = id;
    r._tables = new Map();
    for (const [hid, h] of Object.entries(r.handoffs || {})) {
      for (const [tid, t] of Object.entries(h.tables || {})) {
        if (!r._tables.has(tid)) r._tables.set(tid, { id: tid, owner: hid, columns: t.columns, rows: t.rows });
      }
    }
    for (const [tid, t] of Object.entries((r.run_brief && r.run_brief.tables) || {})) {
      if (!r._tables.has(tid)) r._tables.set(tid, { id: tid, owner: 'RUN_BRIEF', columns: t.columns, rows: t.rows });
    }
    r._cites = new Map();
    r._uses = null;
    r._gapItems = new Map();
    runCache[id] = r;
    return r;
  };

  /* Metadata for a run (issuer, Pathway, state tags): used by the run switcher and the navigator header. */
  WB.runMeta = function (r) {
    const hdr = r._tables.get('snapshot.run_header');
    const row = hdr ? hdr.rows[0] : null;
    const get = (name) => {
      if (!hdr || !row) return '';
      const i = hdr.columns.indexOf(name);
      return i >= 0 ? row[i] : '';
    };
    const steps = r.steps || {};
    const blocked = Object.values(steps).some((s) => s.status === 'blocked' || s.qa_status === 'Blocked');
    let breaches = false;
    for (const f of r.fit || []) for (const ins of f.instruments || []) if (ins.verdict === 'Breaches') breaches = true;
    const tags = [];
    if (r.primary) tags.push('Primary');
    if (r.prior_case) tags.push('Prior Case');
    if (blocked) tags.push('Blocked');
    if (breaches) tags.push('Breaches');
    if (r.fixture && r.fixture.issuer_fictional) tags.push('Fictional');
    if (r.depth === 'quick') tags.push('Quick');
    const analyst = get('analyst');
    return {
      id: r._id,
      issuer: get('issuer') || get('issuer_id'),
      issuerId: get('issuer_id'),
      asOf: get('as_of_date'),
      analyst,
      // the analyst string of a test run carries "(design fixture)": shown as a quiet tag, never as parenthetical text
      analystName: String(analyst || '').replace(/\s*\(design fixture\)\s*/i, ' ').trim(),
      designFixture: /\(design fixture\)/i.test(String(analyst || '')),
      reportDate: get('report_date'),
      objective: get('objective'),
      pathway: WB.PATHWAYS[r.pathway] || r.pathway,
      pathwayKey: r.pathway,
      depth: r.depth,
      primary: !!r.primary,
      frontPage: r.front_page,
      frontPageName: WB.FRONT_PAGES[r.front_page] || r.front_page,
      tags,
    };
  };

  /* ---------- data helpers (all use the current run, WB.run) ---------- */
  WB.handoff = (id) => (WB.run && WB.run.handoffs ? WB.run.handoffs[id] || null : null);
  WB.step = (id) => (WB.run && WB.run.steps ? WB.run.steps[id] || null : null);
  WB.table = (tableId) => (WB.run ? WB.run._tables.get(tableId) || null : null);
  WB.tableOwner = (tableId) => {
    const t = WB.table(tableId);
    return t ? t.owner : null;
  };
  WB.citeModule = (owner) => {
    if (owner === 'RUN_BRIEF') {
      const inp = WB.run.run_brief && WB.run.run_brief.front_matter && WB.run.run_brief.front_matter.inputs;
      return (inp && inp[0]) || 'CP-0';
    }
    return owner;
  };
  WB.cellValue = (table, r, name) => {
    const i = table.columns.indexOf(name);
    return i < 0 ? '' : table.rows[r][i];
  };

  /* Citations: ids are local to a handoff. */
  WB.citation = function (moduleId, id) {
    const key = moduleId + ':' + id;
    if (WB.run._cites.has(key)) return WB.run._cites.get(key);
    const h = WB.handoff(moduleId);
    let found = null;
    if (h) {
      const c = (h.citations || []).find((x) => x.id === id);
      if (c) found = Object.assign({ module: moduleId }, c);
    }
    WB.run._cites.set(key, found);
    return found;
  };

  const CITE_TOKEN = /\[(C\d+(?:\s*,\s*C\d+)*)\]/g;
  WB.CITE_TOKEN_SRC = CITE_TOKEN.source;
  const cacheCite = new Map();
  /* Cite-column parsing: { cites: ['C1', ...], calc: 'formula' | null, note: 'leftover prose' | '' } */
  WB.parseCite = function (raw) {
    const s = raw == null ? '' : String(raw);
    if (cacheCite.has(s)) return cacheCite.get(s);
    const cites = [];
    const re = new RegExp(CITE_TOKEN.source, 'g');
    let m;
    while ((m = re.exec(s))) for (const id of m[1].split(',')) cites.push(id.trim());
    let rest = s.replace(new RegExp(CITE_TOKEN.source, 'g'), ' ');
    let calc = null;
    const ci = rest.indexOf('calc:');
    if (ci >= 0) {
      calc = rest.slice(ci + 5).trim();
      rest = rest.slice(0, ci);
    }
    rest = rest.replace(/[\s—]+/g, ' ').trim();
    const out = { cites: Array.from(new Set(cites)), calc, note: rest.length > 3 ? rest : '', raw: s };
    cacheCite.set(s, out);
    return out;
  };

  const numOf = (v) => {
    const t = String(v).trim();
    const neg = /^\(.*\)/.test(t) || /^[-\u2212]/.test(t);
    const m = /\d[\d,]*\.?\d*/.exec(t);
    if (!m) return null;
    const n = parseFloat(m[0].replace(/,/g, ''));
    return neg ? -n : n;
  };
  const GENERIC = new Set(['change', 'total', 'value', 'pct', 'percentage']);
  /* Which formula in a row's cite computes this cell? Value equality first, then the column's own words in the formula label. */
  WB.pickFormula = function (calc, colName, value) {
    const segs = String(calc || '').split(/calc:\s*/).map((x) => x.trim()).filter(Boolean);
    if (!segs.length) return { formula: null, all: [] };
    const target = numOf(value);
    if (target != null) {
      const hit = segs.find((sg) => {
        const i = sg.lastIndexOf('=');
        const r = i > 0 ? numOf(sg.slice(i + 1)) : null;
        return r != null && Math.abs(r - target) < 1e-9;
      });
      if (hit) return { formula: hit, all: segs };
    }
    const cw = new Set(words(WB.colLabel(colName)).filter((w) => !GENERIC.has(w)));
    const hit = segs.find((sg) => {
      const i = sg.indexOf('=');
      return words(i > 0 ? sg.slice(0, i) : '').some((w) => cw.has(w) && !GENERIC.has(w));
    });
    return { formula: hit || null, all: segs };
  };

  /* Row-level provenance from the cite column. */
  WB.rowInfo = function (table, r) {
    if (!table._rowInfo) table._rowInfo = [];
    if (table._rowInfo[r] !== undefined) return table._rowInfo[r];
    const ci = table.columns.indexOf('cite');
    let info = null;
    if (ci >= 0) {
      const p = WB.parseCite(table.rows[r][ci]);
      const mod = WB.citeModule(table.owner);
      const citations = p.cites.map((id) => WB.citation(mod, id) || { id, module: mod, missing: true });
      const real = citations.filter((c) => !c.missing);
      info = {
        cites: p.cites,
        calc: p.calc,
        note: p.note,
        module: mod,
        citations,
        synthetic: real.some((c) => c.synthetic),
        allSynthetic: real.length > 0 && real.every((c) => c.synthetic),
      };
    }
    table._rowInfo[r] = info;
    return info;
  };

  /* Where each citation is used: analysis paragraphs, table rows, model cells. */
  WB.citationUses = function (moduleId, id) {
    const r = WB.run;
    if (!r._uses) {
      const uses = new Map();
      const add = (mod, cid, place) => {
        const k = mod + ':' + cid;
        if (!uses.has(k)) uses.set(k, []);
        uses.get(k).push(place);
      };
      for (const [hid, h] of Object.entries(r.handoffs || {})) {
        (h.analysis_md || '').split(/\n{2,}/).forEach((para, pi) => {
          const re = new RegExp(CITE_TOKEN.source, 'g');
          let m;
          const seen = new Set();
          while ((m = re.exec(para))) for (const cid of m[1].split(',')) seen.add(cid.trim());
          seen.forEach((cid) => add(hid, cid, { kind: 'analysis', module: hid, para: pi }));
        });
        for (const [tid, t] of Object.entries(h.tables || {})) {
          const ci = t.columns.indexOf('cite');
          if (ci < 0) continue;
          t.rows.forEach((row, ri) => WB.parseCite(row[ci]).cites.forEach((cid) => add(hid, cid, { kind: 'table', module: hid, table: tid, row: ri })));
        }
      }
      for (const [tid, t] of r._tables) {
        if (t.owner !== 'RUN_BRIEF') continue;
        const ci = t.columns.indexOf('cite');
        if (ci < 0) continue;
        const mod = WB.citeModule('RUN_BRIEF');
        t.rows.forEach((row, ri) => WB.parseCite(row[ci]).cites.forEach((cid) => add(mod, cid, { kind: 'table', module: 'RUN_BRIEF', table: tid, row: ri })));
      }
      for (const line of (r.model && r.model.lines) || []) {
        for (const cell of line.cells || []) {
          for (const s of cell.sources || []) add(s.module, s.citation_id, { kind: 'model', module: 'MODEL', line: line.line_id, column: cell.column_id });
        }
      }
      r._uses = uses;
    }
    return r._uses.get(moduleId + ':' + id) || [];
  };

  /* Gaps: items from gaps_md, matched to n/a cells by words. */
  WB.gapItems = function (moduleId) {
    const cache = WB.run._gapItems;
    if (cache.has(moduleId)) return cache.get(moduleId);
    const h = WB.handoff(moduleId);
    const items = [];
    const seenText = new Set();
    if (h && h.gaps_md) {
      const lines = h.gaps_md.split(/\n/).map((l) => l.trim()).filter(Boolean);
      for (const l of lines) {
        if (/^#{1,6}\s/.test(l)) continue;
        const text = l.replace(/^[-*]\s+/, '');
        const ids = Array.from(new Set(text.match(/\bG\d+\b/g) || []));
        let missing = text;
        const colon = text.indexOf(':');
        if (colon > 0 && colon < 110) missing = text.slice(0, colon);
        else {
          const dot = text.indexOf('. ');
          if (dot > 0) missing = text.slice(0, dot);
        }
        // a module's gaps_md can state the same gap twice (the Model repeats its projection note): list it once
        const key = text.replace(/\s+/g, ' ').trim().toLowerCase();
        if (seenText.has(key)) continue;
        seenText.add(key);
        items.push({ module: moduleId, ids, missing: missing.replace(/\s*\(G\d+(?:,\s*G\d+)*\)/g, '').trim(), text });
      }
    }
    cache.set(moduleId, items);
    return items;
  };
  WB.gapsByIds = function (ids) {
    const out = [];
    for (const hid of Object.keys(WB.run.handoffs || {})) {
      for (const it of WB.gapItems(hid)) if (it.ids.some((g) => ids.includes(g))) out.push(it);
    }
    return out;
  };
  const STOP = new Set('the a an of and or in on to for from with by is are not no as at be this that it its per'.split(' '));
  const words = (s) => String(s).toLowerCase().split(/[^a-z0-9]+/).filter((w) => w.length > 2 && !STOP.has(w));
  /* Best gap for an n/a cell: overlap between the cell's row and column words and the gap text.
     A cell that is a Model cell with a reason code is explained by the Model (item stays null, model names the cell).
     A cell neither the gaps nor the Model explain is counted as unresolved (WB.noteUnresolved): the passport says so and lists no gaps. */
  WB.cellGap = function (table, r, c) {
    const mod = WB.citeModule(table.owner);
    const items = WB.gapItems(mod);
    const q = new Set(words(WB.colLabel(table.columns[c]) + ' ' + String(table.rows[r][0]) + ' ' + (table.columns.indexOf('metric_id') >= 0 ? WB.cellValue(table, r, 'metric_id') : '')));
    let best = null;
    let bestScore = 0;
    for (const it of items) {
      const iw = new Set(words(it.text));
      let s = 0;
      q.forEach((w) => iw.has(w) && s++);
      if (s > bestScore) {
        best = it;
        bestScore = s;
      }
    }
    const ref = WB.modelCellFor(table, r, c);
    const mc = ref && WB.modelCell(ref.lineId, ref.columnId);
    const model = mc && mc.value == null && mc.reason ? ref : null;
    const item = bestScore > 0 ? best : null;
    if (!item && !model) WB.noteUnresolved(table, r, c);
    return { item, moduleItems: items, module: mod, model };
  };
  /* n/a cells with no stated reason, per page: window.__wbUnresolvedGaps (array, one entry per cell) and <html data-unresolved>.
     Documented fail-open: this is a fixture-data issue (the module states no gap for the cell), so check.py prints the total and does not fail on it. */
  const unresolved = new Map();
  WB.resetUnresolved = function () {
    unresolved.clear();
    window.__wbUnresolvedGaps = [];
    document.documentElement.dataset.unresolved = '0';
  };
  WB.noteUnresolved = function (table, r, c) {
    const tid = table.twinOf || table.id;
    const key = tid + '|' + r + '|' + c;
    if (unresolved.has(key)) return;
    const entry = { table: tid, row: r, col: table.columns[c], rowLabel: WB.rowLabel(table, r) };
    unresolved.set(key, entry);
    window.__wbUnresolvedGaps = Array.from(unresolved.values());
    document.documentElement.dataset.unresolved = String(unresolved.size);
  };
  window.__wbUnresolvedGaps = [];

  /* ---------- step status (navigator, chips) ---------- */
  WB.stepStatus = function (id) {
    const s = WB.step(id);
    const h = WB.handoff(id);
    if (!s) return 'notrun';
    if (s.status === 'skipped') return 'notrun';
    if (s.status === 'blocked' || s.qa_status === 'Blocked' || (h && h.qa_status === 'Blocked')) return 'blocked';
    const qa = (h && h.qa_status) || s.qa_status;
    if (qa === 'Pass') return 'pass';
    return 'limitations';
  };
  WB.STATUS_WORD = { pass: 'Pass', limitations: 'With limitations', blocked: 'Blocked', notrun: 'Not run' };
  WB.STATUS_TONE = { pass: 'pos', limitations: 'cau', blocked: 'neg', notrun: 'neu' };
  WB.STATUS_ICON = { pass: 'status-pass', limitations: 'status-limited', blocked: 'status-blocked', notrun: 'status-notrun' };
  WB.stepReason = function (id) {
    const s = WB.step(id);
    const st = WB.stepStatus(id);
    if (st === 'notrun') return (s && s.reason) || 'This step did not run in this Pathway.';
    if (st === 'pass') return '';
    const lim = ((WB.run.limitations && WB.run.limitations.cp5) || []).filter((l) => l.module_id === id);
    if (lim.length) return lim.map((l) => l.limitation).join(' ');
    if (s && s.reason) return s.reason;
    const g = WB.gapItems(id);
    if (g.length) return g[0].text;
    return st === 'blocked' ? 'The module did not produce an accepted result.' : '';
  };

  /* ---------- column and cell classification ---------- */
  const ACR = { id: 'ID', ev: 'EV', pd: 'PD', lgd: 'LGD', ltm: 'LTM', ytd: 'YTD', pytd: 'PYTD', fy: 'FY', pf: 'PF', ebitda: 'EBITDA', fcf: 'FCF', cfo: 'CFO', kpi: 'KPI', lme: 'LME', rcf: 'RCF', clo: 'CLO', sofr: 'SOFR', isin: 'ISIN', cusip: 'CUSIP', oid: 'OID', usd: 'USD', cp: 'CP', qa: 'QA', pik: 'PIK', wal: 'WAL', war: 'WAR', dm: 'DM', rq: 'RQ', ssim: 'SSIM', nav: 'NAV', ytw: 'YTW', stw: 'STW', ssn: 'SSN', sn: 'SN', ebit: 'EBIT', bps: 'bps', pct: '%', x: 'x', json: 'JSON', md: 'MD', sha256: 'SHA-256', cr: 'CR', tlb: 'TLB', hy: 'HY', ssim: 'SSIM', cds: 'CDS', gaap: 'GAAP', ebitdar: 'EBITDAR', capex: 'capex', sbc: 'Stock-based compensation', lv: 'Las Vegas' };
  WB.colLabel = function (name) {
    const parts = String(name).split('_');
    const out = [];
    for (const p of parts) {
      const lc = p.toLowerCase();
      out.push(Object.prototype.hasOwnProperty.call(ACR, lc) ? ACR[lc] : lc);
    }
    // a trailing pct or x reads as a unit
    let label = out.join(' ');
    label = label.replace(/ % ?%$/, ' %').replace(/\s+%$/, ' (%)').replace(/\s+x$/, ' (x)');
    return label.charAt(0).toUpperCase() + label.slice(1);
  };
  /* Snake-case keys read as words: net_revenues_q2 becomes "Net revenues, Q2". The raw id stays in the passport. */
  const PERIOD_TOKEN = /^(q[1-4]|h[12]|fy\d{2,4}|ytd|ltm|pytd)$/;
  WB.isSnake = (v) => /^[a-z][a-z0-9]*(_[a-z0-9]+)+$/.test(String(v));
  /* context: the row's own text. A word the context writes with a capital mid-sentence keeps it ("las_vegas" reads "Las Vegas"). */
  /* an id read as words: a single lowercase token of an id column ("revenue", "sbc") becomes a word, acronyms in capitals;
     snake ids go through WB.humanize. Only for id columns and row labels: a text cell's own lowercase words stay as served. */
  WB.humanizeId = function (v, context) {
    const str = String(v);
    if (/^[a-z][a-z0-9]*$/.test(str)) return Object.prototype.hasOwnProperty.call(ACR, str) ? ACR[str] : str.charAt(0).toUpperCase() + str.slice(1);
    return WB.humanize(str, context);
  };
  WB.humanize = function (v, context) {
    const str = String(v);
    if (!WB.isSnake(str)) return str;
    const toks = str.split('_');
    let period = '';
    if (toks.length > 1 && PERIOD_TOKEN.test(toks[toks.length - 1])) period = toks.pop().toUpperCase();
    const proper = (t) => {
      if (!context || t.length < 3) return t;
      const m = new RegExp('[a-z,;] (' + t.charAt(0).toUpperCase() + t.slice(1) + ')\\b').exec(context);
      return m ? m[1] : t;
    };
    const out = toks.map((t) => (Object.prototype.hasOwnProperty.call(ACR, t) ? ACR[t] : proper(t))).join(' ');
    return out.charAt(0).toUpperCase() + out.slice(1) + (period ? ', ' + period : '');
  };
  WB.HUMAN_ID_COLS = /^(metric_id|kpi_id|driver_id|check|check_id|addback_id|assumption_id|line_id|slot_id)$/;
  const NUM_RE = /^[(\-−+]?\$?\d[\d,]*(\.\d+)?\)?\s?(%|x|pp|bps|m|bn)?$|^[(\-−+]?\.\d+\)?%?$/;
  WB.isNumeric = (v) => NUM_RE.test(String(v).trim());
  WB.isEmpty = (v) => {
    const s = String(v == null ? '' : v).trim();
    return s === '' || s === '—' || s === '-' || /^n\/a$/i.test(s);
  };
  const ID_COL = /(^|_)(id|ids|code|isin|cusip|date|name|file|sha256|ticker|module|run_id|period|fiscal_year|fiscal_quarter|year|days|day_count|quarter|slot|case)(_|$)/;
  /* a value that reads as a code (no spaces, and digits, separators or capitals in it) or starts with an ISO date */
  const codeLike = (v) => {
    const s = String(v).trim();
    if (/^\d{4}-\d{2}-\d{2}/.test(s)) return true;
    if (/\s/.test(s)) return false;
    // a single token is a code unless it is a capitalised word (a name such as "Moody's" or "Regional")
    return !/^[A-Z][a-z'’]+$/.test(s);
  };
  const PERIOD_ID = /^(LTM_)?(Q[1-4]|H[12]|FY)_?\d{4}$/;
  WB.PERIOD_ID = PERIOD_ID;
  /* period ids read as periods: Q2_2026 becomes Q2 2026, LTM_Q2_2026 becomes LTM Q2 2026 */
  WB.periodLabel = (v) => String(v).replace(/^(LTM_)?(Q[1-4]|H[12]|FY)_?(\d{4})$/, (m0, l, a, y) => (l ? 'LTM ' : '') + (a === 'FY' ? 'FY' + y : a + ' ' + y));
  /* scenario and case enums read as words: BASE becomes Base (three-letter acronyms such as LME stay) */
  WB.enumWord = (v) => (/^[A-Z]{4,}$/.test(String(v)) ? String(v).charAt(0) + String(v).slice(1).toLowerCase() : String(v));
  WB.SCALE_COLS = new Set(['status', 'qa_status', 'severity', 'confidence', 'fit_verdict', 'verdict', 'recommendation', 'valuation', 'credit_score', 'credit_direction', 'sector_outlook', 'pressure', 'probability', 'impact', 'feasibility', 'preference', 'compensation_vs_risk', 'alignment', 'calculation_status', 'trend', 'final', 'cap', 'uncapped', 'recommendation_cap', 'likelihood_direction', 'sponsor_quality', 'materiality', 'evidence_quality', 'priming_risk', 'recovery_sensitivity', 'creditor_risk', 'freshness', 'traceability', 'treatment', 'pressure_class', 'likelihood_class', 'prior', 'outcome', 'fulcrum', 'position', 'assessment', 'evidence_status', 'disposition', 'comparability', 'blocking']);
  /* scale columns whose values a deterministic rule produces (calculated), not a judgement */
  WB.CALC_SCALE = new Set(['fit_verdict', 'cap', 'recommendation_cap', 'qa_status', 'calculation_status', 'freshness', 'position', 'fulcrum']);
  const MODEL_COLS = /(analyst_|implication|rationale|thesis|reason|effect|interpretation|consequence|why_|^why$|summary|explanation|key_reason|answer|uncertainty|what_would|watch_trigger|monitoring|counter_|open_question|primary_support|primary_downside|^text$|transmission|mechanism|required_fix|finding|catalyst|assessment|credit_impact|pd_lgd_effect|creditor_risk)/i;
  const KNOWN_EXTRA = new Set(['not computable', 'not met', 'met', 'neutral', 'stable', 'up', 'down', 'flat', 'new', 'unchanged', 'verified', 'calculated', 'reported', 'above', 'below', 'unknown', 'n/a', 'avoid', 'yes', 'no', 'requires more work', 'insufficient_information', 'mixed']);
  WB.isScaleValue = function (v) {
    const lc = String(v).trim().toLowerCase();
    if (/^v?\d - /.test(lc) || /^(high|medium|low)$/.test(lc) || KNOWN_EXTRA.has(lc)) return true;
    return ['pos', 'cau', 'neg'].some((t) => TONE_WORDS[t].includes(lc));
  };
  WB.columnKinds = function (table) {
    if (table._cols) return table._cols;
    const uniform = (name) => {
      const i = table.columns.indexOf(name);
      if (i < 0 || !table.rows.length) return null;
      const v = table.rows[0][i];
      return table.rows.every((r) => r[i] === v) ? v : null;
    };
    const cur = uniform('currency');
    const unit = uniform('unit');
    table._unitNote = { currency: cur, unit };
    const kinds = table.columns.map((name, c) => {
      const vals = table.rows.map((r) => r[c]).filter((v) => !WB.isEmpty(v));
      const label = WB.colLabel(name);
      let kind = 'text';
      if (name === 'cite') kind = 'hidden';
      else if ((name === 'currency' && cur) || (name === 'unit' && unit)) kind = 'hidden';
      else if (WB.SCALE_COLS.has(name) && vals.length && vals.filter(WB.isScaleValue).length / vals.length >= 0.5) kind = 'scale';
      else if (WB.SCALE_COLS.has(name) && !vals.length) kind = 'scale';
      else if (ID_COL.test(name)) kind = 'id';
      else if (vals.length && vals.filter(WB.isNumeric).length / vals.length >= 0.6) kind = 'numeric';
      else if (vals.length && (vals.some((v) => String(v).length > 70) || vals.reduce((a, v) => a + String(v).length, 0) / vals.length > 46)) kind = 'prose';
      const out = { name, label, kind, modelWritten: MODEL_COLS.test(name) && (kind === 'prose' || kind === 'text'), index: c };
      if (kind === 'id') {
        // an id column whose values are names (bond names, KPI labels, scenario words) reads as text, not as a code
        out.textual = vals.length > 0 && vals.filter(codeLike).length / vals.length < 0.6;
        out.periodIds = vals.length > 0 && vals.every((v) => PERIOD_ID.test(String(v)));
        if (WB.HUMAN_ID_COLS.test(name) || out.textual || out.periodIds) out.label = label.replace(/ ID$/, '');
      }
      return out;
    });
    table._cols = kinds;
    return kinds;
  };
  WB.unitLabel = function (currency, unit) {
    const cur = { USD: 'US$', EUR: '€', GBP: '£' }[currency] || currency || '';
    const u = { MILLIONS: 'm', THOUSANDS: 'k', BILLIONS: 'bn', UNITS: '' }[unit];
    const un = u == null ? unit || '' : u;
    return (cur + (cur && un ? ' ' : '') + un).trim();
  };
  WB.tableUnit = function (table) {
    WB.columnKinds(table);
    const n = table._unitNote;
    if (n.currency || n.unit) return WB.unitLabel(n.currency, n.unit);
    return '';
  };

  /* ---------- formatting: as served, grouped thousands, negatives in parentheses ---------- */
  const FMT_RE = /^([-−+]?)(\$?)(\d[\d,]*)(\.\d+)?(%|x|pp|bps|m|bn)?$/;
  /* opts.group: the value is an amount, so a four-digit figure such as 2018 is grouped (2,018) rather than read as a year */
  WB.fmtNum = function (s, opts) {
    const str = String(s).trim();
    if (/^\(.*\)/.test(str)) return str;
    const m = FMT_RE.exec(str);
    if (!m) return str;
    let [, sign, dollar, int, dec, suf] = m;
    const digits = int.replace(/,/g, '');
    const yearLike = digits.length === 4 && /^(19|20)\d\d$/.test(digits) && !dec && !(opts && opts.group);
    if (digits.length >= 5 || (digits.length === 4 && !yearLike)) int = digits.replace(/\B(?=(\d{3})+(?!\d))/g, ',');
    const body = dollar + int + (dec || '');
    const neg = sign === '-' || sign === '−';
    if (neg) return '(' + body + ')' + (suf || '');
    return (sign === '+' ? '+' : '') + body + (suf || '');
  };
  /* Numbers by unit, for call lines, tiles and table cells (the run is never changed; the passport keeps the served value, grouped, under "Served as"):
     yields and spreads-as-percent to 2 dp, prices to 2 dp, amounts in US$m as whole millions with grouping. Anything else prints as served (WB.fmtNum). */
  const YIELD_COL = /^(yield_pct|yield_or_dm|talk_(low|mid|high)|implied_(low|mid|high)|comparable_level)$/;
  const PRICE_COL = /^(bid|ask|mid|price)$/;
  const NOT_AMOUNT = /(_x$|_pct|pct_|multiple|ratio|cover|leverage|margin|growth|share|rate|bps|headroom|weight|probab|score|days|months|count|years|year|period|dm$|spread|coupon|oid|floor|cap$)/;
  const AMOUNT_UNIT = /^(USD m|US\$ ?m|USD millions|MILLIONS)$/i;
  WB.fmtByUnit = function (table, r, c) {
    const name = table.columns[c];
    const raw = String(table.rows[r][c]).trim();
    const m = /^([-−]?)(\d[\d,]*)(\.\d+)?(%?)$/.exec(raw);
    if (!m) return null;
    const val = parseFloat(m[2].replace(/,/g, '') + (m[3] || ''));
    if (!isFinite(val)) return null;
    const neg = m[1] !== '';
    const basisCol = table.columns.indexOf('metric_basis');
    const basis = basisCol >= 0 ? String(table.rows[r][basisCol]) : '';
    const group = (n) => String(n).replace(/\B(?=(\d{3})+(?!\d))/g, ',');
    // a yield: yield_pct is always a percent; the other yield columns are percents when the value carries decimals or a yield basis
    // (a discount margin is whole bps and stays as served)
    if (YIELD_COL.test(name) && (name === 'yield_pct' || m[4] === '%' || m[3] || /^(YT[WMCP]|YTW)$/.test(basis))) {
      return (neg ? '-' : '') + val.toFixed(2) + m[4];
    }
    if (PRICE_COL.test(name) && (m[3] || /^\d{2,3}$/.test(m[2])) && val < 1000 && m[4] === '') {
      return (neg ? '-' : '') + val.toFixed(2);
    }
    // amounts in US$m: whole millions with grouping, negatives in parentheses
    const unitCol = table.columns.indexOf('unit_label');
    const rowUnit = unitCol >= 0 ? String(table.rows[r][unitCol]) : null;
    // a chart's twin table names no unit of its own: it takes the unit of the table it was cut from
    const src = table.twinOf ? WB.table(table.twinOf) : null;
    const tUnit = WB.tableUnit(table) || (src ? WB.tableUnit(src) : '');
    if (!NOT_AMOUNT.test(name) && (rowUnit != null ? AMOUNT_UNIT.test(rowUnit) : /^US\$ ?m$/.test(tUnit)) && m[4] === '') {
      const whole = Math.round(val);
      return neg && whole ? '(' + group(whole) + ')' : group(whole);
    }
    return null;
  };

  /* ---------- signals: tone, icon and word for scale values ---------- */
  const HIGH_BAD = new Set(['severity', 'pressure', 'probability', 'impact', 'materiality', 'priming_risk', 'recovery_sensitivity', 'creditor_risk', 'likelihood_class', 'pressure_class']);
  const HIGH_GOOD = new Set(['confidence', 'feasibility', 'evidence_quality']);
  const TONE_WORDS = {
    pos: ['pass', 'fits', 'headroom', 'improving', 'improved', 'aligned', 'attractive', 'very attractive', 'preferred', 'supported', 'traceable', 'sufficient', 'current', 'positive', 'available', 'audited'],
    cau: ['restricted', 'with limitations', 'watch', 'tight', 'unclear', 'divergent', 'partly traceable', 'partial', 'stale', 'adequate', 'challenged', 'requires more work', 'mixed', 'fair', 'insufficient_information'],
    neg: ['blocked', 'breaches', 'breached', 'deteriorating', 'deteriorated', 'avoid', 'inadequate', 'rejected', 'untraceable', 'missing', 'negative'],
  };
  WB.signal = function (value, col) {
    const v = String(value).trim();
    const lc = v.toLowerCase();
    const out = { tone: 'neu', icon: null, word: v, ordinal: 0 };
    if (WB.isEmpty(v) && lc !== 'n/a') return { tone: 'neu', icon: null, word: '—', ordinal: 0 };
    // ordinal High / Medium / Low
    if (/^(high|medium|low)$/.test(lc) && (HIGH_BAD.has(col) || HIGH_GOOD.has(col) || col === undefined)) {
      const level = lc === 'high' ? 3 : lc === 'medium' ? 2 : 1;
      const bad = !HIGH_GOOD.has(col);
      const tone = level === 2 ? 'cau' : (level === 3) === bad ? 'neg' : 'pos';
      return { tone, icon: 'bars', word: v, ordinal: level };
    }
    // house scales with a leading position
    let m = /^(\d) - (.+)$/.exec(v);
    if (m) {
      const n = +m[1];
      return { tone: n <= 2 ? 'pos' : n === 3 ? 'cau' : 'neg', icon: null, word: v, pos: m[1], label: m[2], scalePos: n };
    }
    m = /^V(\d) - (.+)$/.exec(v);
    if (m) {
      const n = +m[1];
      return { tone: n <= 2 ? 'pos' : n === 3 ? 'cau' : 'neg', icon: null, word: v, pos: 'V' + m[1], label: m[2], scalePos: n };
    }
    if (lc === 'avoid') return { tone: 'neg', icon: 'cross', word: v, pos: 'A', label: 'Avoid' };
    if (lc === 'n/a') return { tone: 'neu', icon: null, word: 'N/A', pos: '—', label: 'N/A' };
    if (col === 'calculation_status' || col === 'position' || col === 'disposition' || col === 'blocking') return { tone: 'neu', icon: null, word: v };
    if (lc === 'met') return { tone: 'neg', icon: 'gauge', word: v };
    if (lc === 'not met') return { tone: 'pos', icon: 'gauge', word: v };
    if (lc === 'yes' && col === 'fulcrum') return { tone: 'neg', icon: 'cross', word: v };
    if (lc === 'no' && col === 'fulcrum') return { tone: 'neu', icon: null, word: v };
    const dirIcon = { up: 'arrow-up', down: 'arrow-down', flat: 'arrow-flat', improving: 'arrow-up', deteriorating: 'arrow-down', stable: 'arrow-flat', improved: 'arrow-up', deteriorated: 'arrow-down', unchanged: 'arrow-flat', new: 'plus', removed: 'minus' };
    let tone = 'neu';
    for (const t of ['pos', 'cau', 'neg']) if (TONE_WORDS[t].includes(lc)) tone = t;
    if (lc === 'restricted') out.word = 'With limitations';
    if (lc === 'fair' || lc === 'stable' || lc === 'neutral' || lc === 'unchanged' || lc === 'new' || lc === 'up' || lc === 'down' || lc === 'flat') tone = lc === 'fair' ? 'cau' : 'neu';
    let icon = dirIcon[lc] || null;
    if (!icon) {
      icon = tone === 'pos' ? 'tick' : tone === 'cau' ? 'warn' : tone === 'neg' ? 'cross' : null;
      if (lc === 'restricted' || lc === 'with limitations') icon = 'status-limited';
      if (lc === 'blocked') icon = 'status-blocked';
      if (lc === 'pass') icon = 'status-pass';
    }
    out.tone = tone;
    out.icon = icon;
    if (col === 'trend') out.tone = 'neu';
    return out;
  };

  /* A portfolio limit's state, one rule for every view: Breached as served; Within with headroom under 10% of the limit is Tight. */
  WB.limitState = function (status, limit, current) {
    const s = String(status || '');
    const lim = parseFloat(String(limit).replace(/,/g, ''));
    const cur = parseFloat(String(current).replace(/,/g, ''));
    if (s === 'Breached') return { tone: 'neg', icon: 'cross', word: 'Breached' };
    if (s === 'Within') {
      if (isFinite(lim) && isFinite(cur) && lim > 0 && (lim - cur) / lim < 0.1) return { tone: 'cau', icon: 'warn', word: 'Tight' };
      return { tone: 'pos', icon: 'status-pass', word: 'Within' };
    }
    return { tone: 'neu', icon: 'info', word: s || 'Not stated' };
  };

  /* A claim class in words, from the claims register (C2-1L becomes "First-lien claims"); the id when the register has no row. */
  WB.claimName = function (classId) {
    const t = WB.table('cp4c.claims_register');
    if (!t) return String(classId);
    const ci = t.columns.indexOf('class_id');
    const ni = t.columns.indexOf('claim');
    const row = ci >= 0 && ni >= 0 ? t.rows.find((r) => r[ci] === classId) : null;
    return row ? String(row[ni]).replace(/\s*\([^)]*\)\s*$/, '').trim() : String(classId);
  };

  /* ---------- provenance per cell ---------- */
  const SNAP_SLOTS = { fy_2: 'FY-2', fy_1: 'FY-1', fy: 'FY', pytd: 'PYTD', ytd: 'YTD', ltm: 'LTM' };
  /* the columns of the Model strip tables (model.metrics, model.summary) by their Model column kind; the three FY columns are the last three FYs */
  const MODEL_KIND = { fy_2: ['FY', 2], fy_1: ['FY', 1], fy: ['FY', 0], pytd: ['PYTD', 0], ytd: ['YTD', 0], ltm: ['LTM', 0], pf_ltm: ['PF_LTM', 0] };
  function modelColumnId(name) {
    const spec = MODEL_KIND[name];
    const cols = (WB.run.model && WB.run.model.columns) || [];
    if (!spec) return null;
    const of = cols.filter((x) => x.kind === spec[0]);
    const col = of[of.length - 1 - spec[1]];
    return col ? col.column_id : null;
  }
  /* the Model cell behind a table cell: the Snapshot financials and the Model strip tables carry Model lines by id */
  WB.modelCellFor = function (table, r, c) {
    const tid = table.twinOf || table.id;
    const name = table.columns[c];
    if (tid === 'snapshot.financials') {
      const slot = SNAP_SLOTS[name];
      if (!slot) return null;
      const colId = WB.run.model && WB.run.model.snapshot_columns && WB.run.model.snapshot_columns[slot];
      const lineId = WB.cellValue(table, r, 'line_id');
      return colId && lineId ? { lineId, columnId: colId } : null;
    }
    if (tid === 'model.summary' || tid === 'model.metrics') {
      const id = WB.cellValue(table, r, tid === 'model.summary' ? 'line_id' : 'metric_id');
      const colId = modelColumnId(name);
      const lineId = id ? (tid === 'model.metrics' ? 'metric:' + id : id) : null;
      return colId && lineId && WB.modelLine(lineId) ? { lineId, columnId: colId } : null;
    }
    return null;
  };
  WB.modelLine = (lineId) => ((WB.run.model && WB.run.model.lines) || []).find((l) => l.line_id === lineId) || null;
  WB.modelCell = function (lineId, columnId) {
    const line = WB.modelLine(lineId);
    if (!line) return null;
    return (line.cells || []).find((x) => x.column_id === columnId) || null;
  };
  const HOST_OWNERS = new Set(['MODEL', 'PROJECTION', 'FIT']);
  /* table id -> the numeric column that holds a judgement (content doc 04: the protection score is an illustrative five-point scale) */
  WB.JUDGEMENT_NUMERIC = { 'cp4.protection_score': 'score' };
  const DATE_COL = /(^|_)date(_|$)/;
  WB.DATE_COL = DATE_COL; // a date value (a level date, an event date) is a stated value like any text; other id columns name things
  const RATING_COL = /(^|_)(rating|ratings|outlook)(_|$)/;
  const HOST_DERIVED = /(multiple|_pct$|pct_|_x$|ratio|leverage|cover|margin|growth|share|headroom|max_size|exposure_pct)/;

  /* Origin of one cell: { kind, row, ... }. kind is cited | calculated | synthetic | model | illustrative | gap | none | plain */
  WB.cellOrigin = function (table, r, c) {
    const kinds = WB.columnKinds(table);
    const col = kinds[c];
    const v = table.rows[r][c];
    if (col.kind === 'hidden') return { kind: 'plain' };
    if (col.kind === 'scale') {
      if (WB.isEmpty(v) && String(v).toLowerCase() !== 'n/a') return { kind: 'gap' };
      const key = col.name + ':' + table.id;
      const calc = WB.CALC_SCALE.has(col.name) || (table.id === 'cp4.covenant_tests' && col.name === 'status');
      if (calc || (HOST_OWNERS.has(table.owner) && col.name !== 'recommendation' && col.name !== 'valuation')) return { kind: 'calculated', scale: true, info: WB.rowInfo(table, r) };
      return { kind: 'illustrative', scale: true, key };
    }
    if (WB.isEmpty(v)) {
      // an n/a that is a Model cell with a reason code resolves to that Model cell (its passport shows the code and the full reason)
      const gref = WB.modelCellFor(table, r, c);
      const gmc = gref && WB.modelCell(gref.lineId, gref.columnId);
      return gmc && gmc.value == null ? { kind: 'gap', model: gref } : { kind: 'gap' };
    }
    if (col.kind === 'id' && !DATE_COL.test(col.name)) return { kind: 'plain' };
    if (col.name === 'cr_score') return { kind: 'illustrative', key: 'cr_score' };
    // numeric judgements: a score a module assigns (lender protection by area) is illustrative, whatever evidence the row cites
    if (WB.JUDGEMENT_NUMERIC[table.twinOf || table.id] === col.name) return { kind: 'illustrative', key: col.name + ':' + table.id, info: WB.rowInfo(table, r) };
    const info = WB.rowInfo(table, r);
    if (col.kind === 'prose' || (col.kind === 'text' && col.modelWritten)) {
      if (col.modelWritten) return { kind: 'model', info };
      return { kind: info && info.cites.length ? (info.synthetic ? 'synthetic' : 'cited') : 'plain', info };
    }
    if (col.kind === 'text' || col.kind === 'id') {
      // a short text value takes the provenance of its row, like prose and numbers do: a row that cites a source gives it that source's mark
      // and passport (cited or synthetic); plain only when the row cites nothing. The row-label column of a table and unit descriptors name
      // things rather than state values, so they stay plain. An agency rating or outlook is always a figure: with no source it reads "no source stated".
      const lead = kinds.findIndex((k) => k.kind !== 'hidden' && !/_id$/.test(k.name));
      if (/^(unit_label|unit|currency)$/.test(col.name) || (table.rows.length > 1 && c === lead)) return { kind: 'plain' };
      if (info && info.cites.length) return { kind: info.synthetic ? 'synthetic' : 'cited', info };
      if (RATING_COL.test(col.name)) return { kind: 'none', info };
      return { kind: 'plain' };
    }
    // numeric: a Model line cell carries its own basis; derived columns of host tables are calculated
    const mcRef = WB.modelCellFor(table, r, c);
    if (mcRef) {
      const mc = WB.modelCell(mcRef.lineId, mcRef.columnId);
      if (mc && mc.value != null) {
        const syn = (mc.sources || []).some((src) => {
          const ci = WB.citation(src.module, src.citation_id);
          return ci && ci.synthetic;
        });
        return { kind: mc.basis === 'REPORTED' ? (syn ? 'synthetic' : 'cited') : 'calculated', model: mcRef, basis: mc.basis, info };
      }
    }
    if (!info) {
      if (HOST_OWNERS.has(table.owner)) return { kind: 'calculated', host: true };
      return { kind: 'none', register: true };
    }
    if (HOST_OWNERS.has(table.owner) && HOST_DERIVED.test(col.name)) return { kind: 'calculated', host: true, info };
    if (info.calc && !info.cites.length) return { kind: 'calculated', info };
    if (info.calc) {
      // both: a number that appears as an operand of the formula is an input (cited); the rest are derived
      const num = String(v).replace(/[^0-9.\-]/g, '').replace(/^-/, '');
      const lhs = info.calc.lastIndexOf('=') > 0 ? info.calc.slice(0, info.calc.lastIndexOf('=')) : info.calc;
      const operands = (lhs.match(/\d[\d,]*\.?\d*/g) || []).map((x) => x.replace(/,/g, ''));
      const isOperand = num && operands.includes(num);
      if (isOperand) return { kind: info.synthetic ? 'synthetic' : 'cited', info };
      return { kind: 'calculated', info };
    }
    if (info.cites.length) return { kind: info.synthetic ? 'synthetic' : 'cited', info };
    return { kind: 'none', info };
  };

  /* ---------- refs: descriptors behind every figure, resolved lazily when selected ---------- */
  const refs = new Map();
  let refSeq = 0;
  WB.ref = function (desc) {
    const key = 'r' + ++refSeq;
    refs.set(key, desc);
    return key;
  };
  WB.getRef = (key) => refs.get(key);
  WB.clearRefs = () => refs.clear();

  /* The passport: everything the inspector shows for one descriptor. */
  const ORIGIN_NOTE = {
    cited: 'Read from a document in the Source Pack.',
    calculated: 'Computed by a deterministic script from the inputs below.',
    synthetic: 'TEST DATA: a value the sources cannot supply, invented for the design. Not a fact about the issuer.',
    model: 'Written by the model. Figures inside the text stay clickable to their own sources.',
    illustrative: 'A judgement no RBOT run has produced yet. Every test run is a design fixture, so this value is illustrative.',
    gap: 'The sources cannot support this figure. It is shown as missing, never as zero.',
    none: 'The row names no source.',
  };
  WB.ORIGIN_NOTE = ORIGIN_NOTE;

  /* the other values of a row in words ("Line Equity · Basis Market"), for a passport that has no source to show */
  WB.rowContextText = function (table, r, c) {
    const out = [];
    WB.columnKinds(table).forEach((k) => {
      if (k.kind === 'hidden' || k.index === c || out.length >= 4) return;
      const v = table.rows[r][k.index];
      if (WB.isEmpty(v) || k.kind === 'prose' || String(v).length > 48 || /[a-z]_[a-z]/.test(String(v))) return; // machine ids stay out of the sentence
      out.push(k.label + ' ' + (k.kind === 'numeric' ? WB.fmtNum(v, { group: true }) : WB.humanize(String(v))));
    });
    return out.join(' \u00B7 ');
  };

  function citeChip(c) {
    return { id: c.id, module: c.module, label: (c.source || '') + (c.locator ? ' · ' + c.locator : ''), synthetic: !!c.synthetic, missing: !!c.missing, desc: { t: 'cite', module: c.module, id: c.id } };
  }
  WB.citeChipData = citeChip;

  /* the label of a row in words: the first visible column, humanised (snake ids and period ids read as words) */
  WB.rowLabel = function (table, r) {
    const kinds = WB.columnKinds(table);
    const lead = kinds.find((k) => k.kind !== 'hidden' && !/^(facility_id|portfolio_id)$/.test(k.name)) || kinds.find((k) => k.kind !== 'hidden');
    if (!lead) return '';
    const v = String(table.rows[r][lead.index] == null ? '' : table.rows[r][lead.index]);
    if (WB.PERIOD_ID.test(v)) return WB.periodLabel(v);
    return lead.kind === 'id' ? WB.humanizeId(v) : WB.humanize(v);
  };
  /* where a table lives, in words: "Protection score by area chart, from Protection score · Covenants and legal (CP-4)" */
  WB.tableWhere = function (table) {
    const owner = table.owner;
    const mod = owner === 'RUN_BRIEF' ? 'Run Brief' : WB.moduleName(owner) + (/^CP-/.test(owner) ? ' (' + owner + ')' : '');
    const base = WB.tableTitle(table.twinOf || table.id);
    return (table.chartId ? WB.chartTitle(table.chartId) + ' chart, from ' : '') + base + ' · ' + mod;
  };

  /* an integer part in thousands groups, the rest as served: "17600.082" reads "17,600.082", "-37.5" stays "-37.5" */
  WB.groupServed = function (v) {
    const str = String(v == null ? '' : v);
    const m = /^([-−+]?\$?)(\d{4,})(\.\d+)?(%|x|pp|bps)?$/.exec(str.trim());
    return m ? m[1] + m[2].replace(/\B(?=(\d{3})+(?!\d))/g, ',') + (m[3] || '') + (m[4] || '') : str;
  };
  /* a citation's origin locator in words ("data:C177" reads "Data supplied to the run"); the raw locator goes to the passport foot */
  WB.originInWords = function (origin) {
    const s = String(origin || '');
    let m = /^doc:.+:(\d+)$/.exec(s);
    if (m) return 'A document in the Source Pack, line ' + m[1];
    if (/^data:/.test(s)) return 'Data supplied to the run';
    m = /^(CP-[0-9A-Z]+):C\d+$/.exec(s);
    if (m) return 'Carried from ' + WB.moduleName(m[1]) + ' (' + m[1] + ')';
    m = /^caos:[^/]+\/(CP-[0-9A-Z]+)#\d+$/.exec(s);
    if (m) return 'Output of the CAOS run: ' + WB.moduleName(m[1]) + ' (' + m[1] + ')';
    if (/^synthetic:/.test(s)) return 'A synthetic fixture value, invented for the design';
    return s ? 'Recorded in the run file' : '';
  };

  WB.buildPassport = function (d) {
    const P0 = { kind: 'none', title: '', code: '', id: '', sub: '', fields: [], formula: null, inputs: [], excerpt: null, cites: [], usedIn: null, gaps: [], gapChips: [], note: '', table: null, chart: null };
    if (!d) return Object.assign(P0, { title: 'Nothing selected' });
    if (d.t === 'cite') {
      const c = WB.citation(d.module, d.id);
      if (!c) return Object.assign(P0, { kind: 'none', code: d.id, title: 'Citation ' + d.id + ' is not in ' + WB.moduleName(d.module), note: 'The handoff for ' + d.module + ' lists no citation with this id.' });
      const uses = WB.citationUses(d.module, d.id);
      return Object.assign(P0, {
        kind: c.synthetic ? 'synthetic' : 'cited',
        code: c.id,
        title: c.source,
        sub: WB.moduleName(d.module) + ' · ' + d.module,
        fields: [
          ['File', c.source, true],
          ['Locator', c.locator, true],
          ['Anchored', c.anchored ? 'Yes, excerpt found at the locator' : 'No, excerpt not anchored to the file', false],
          ['Origin', WB.originInWords(c.origin), false],
        ],
        id: c.origin || '',
        excerpt: c.excerpt,
        usedIn: uses.length,
        usedPlaces: uses,
        evidenceAnchor: 'ev-' + WB.cssId(d.module + '-' + d.id),
        note: c.synthetic ? ORIGIN_NOTE.synthetic : '',
      });
    }
    if (d.t === 'cell') {
      const table = WB.table(d.table);
      if (!table) return Object.assign(P0, { title: 'Table ' + d.table + ' is not in this run' });
      const o = WB.cellOrigin(table, d.r, d.c);
      if (o.model) {
        const pm = WB.buildPassport({ t: 'mcell', lineId: o.model.lineId, columnId: o.model.columnId });
        pm.table = { id: d.table, row: d.r, col: d.c };
        return pm;
      }
      const kinds = WB.columnKinds(table);
      const col = kinds[d.c];
      const value = table.rows[d.r][d.c];
      const rowLabel = WB.rowLabel(table, d.r);
      const where = WB.tableWhere(table);
      // the figure in words: the label the page shows (d.label) or its row and column; a "—" row label is dropped; the owner table and module underneath; the raw id stays small at the foot
      const colWord = d.label || col.label;
      const rowWord = d.label || WB.isEmpty(rowLabel) ? '' : rowLabel;
      const p = Object.assign(P0, {
        kind: o.kind === 'plain' ? 'none' : o.kind,
        code: '',
        id: d.table + ' · row ' + (d.r + 1) + ' · ' + col.name,
        title: rowWord && rowWord !== String(value) ? rowWord + ' · ' + colWord : colWord,
        sub: where,
        fields: [['Served as', WB.groupServed(value), true]],
        table: { id: d.table, row: d.r, col: d.c },
        note: ORIGIN_NOTE[o.kind] || '',
      });
      const unit = WB.tableUnit(table);
      if (unit) p.fields.push(['Unit', unit, false]);
      const info = o.info || (o.kind !== 'gap' ? WB.rowInfo(table, d.r) : null);
      if (o.kind === 'gap') {
        const g = WB.cellGap(table, d.r, d.c);
        p.fields = [['Missing', colWord + (rowWord ? ' for ' + rowWord : ''), false]];
        if (g.item) {
          p.gaps = [g.item];
          p.fields.push(['Reason', g.item.text, false]);
        } else {
          // no gap matches this cell and no Model cell explains it: say so, list no gaps (the module's other gaps do not apply to it)
          p.fields.push(['Reason', 'Reason not recorded by the module', false]);
        }
        p.sub = p.sub || WB.moduleName(g.module);
        return p;
      }
      if (info) {
        p.cites = info.citations.map(citeChip);
        const first = (o.kind === 'synthetic' ? info.citations.find((c) => !c.missing && c.synthetic) : info.citations.find((c) => !c.missing && !c.synthetic)) || info.citations.find((c) => !c.missing);
        if (o.kind === 'cited' || o.kind === 'synthetic') {
          if (first) {
            p.excerpt = first.excerpt;
            p.fields.push(['File', first.source, true], ['Locator', first.locator, true]);
            p.usedIn = WB.citationUses(first.module, first.id).length;
          }
        }
        if (info.synthetic && o.kind !== 'synthetic' && o.kind !== 'calculated') p.note += ' This row also cites synthetic data.';
      }
      if (o.kind === 'calculated' && info && info.calc) {
        const pf = WB.pickFormula(info.calc, col.name, value);
        p.formula = pf.formula;
        if (!pf.formula) {
          p.note = 'Derived in the same row. The row states a formula for another figure, shown here for reference: ' + pf.all.join('; ');
        }
        // inputs: sibling cells whose number appears in the formula, then the cited sources
        const operands = new Set(((pf.formula || '').match(/\d[\d,]*\.?\d*/g) || []).map((x) => x.replace(/,/g, '')));
        kinds.forEach((k, ci) => {
          if (ci === d.c || k.kind !== 'numeric') return;
          const sv = String(table.rows[d.r][ci]).replace(/[^0-9.]/g, '');
          // a sibling input reads as its column label and value (refinement 1: inputs labelled, never bare glyphs)
          if (sv && operands.has(sv)) p.inputs.push({ id: k.label, label: WB.fmtNum(table.rows[d.r][ci], { group: true }) + (rowLabel ? ' · ' + rowLabel : ''), desc: { t: 'cell', table: d.table, r: d.r, c: ci } });
        });
        for (const c of info.citations) if (!c.missing) p.inputs.push({ id: c.id, label: (c.source || '') + (c.locator ? ' \u00B7 ' + c.locator : ''), desc: { t: 'cite', module: c.module, id: c.id } });
      }
      if (o.kind === 'calculated' && o.host) {
        p.formula = null;
        p.note = 'Computed by the host script from the Model (rbot-model/1). This table carries no citation column; the Model line carries the sources.';
        if (o.model) {
          const mc = WB.modelCell(o.model.lineId, o.model.columnId);
          const line = WB.modelLine(o.model.lineId);
          if (mc && line) {
            p.inputs.push({ id: line.line_id, label: line.label + ' · ' + (mc.basis || mc.reason || ''), desc: { t: 'mcell', lineId: o.model.lineId, columnId: o.model.columnId } });
            if (line.formula) p.formula = line.formula;
          }
        }
      }
      if (o.kind === 'illustrative') {
        p.note = ORIGIN_NOTE.illustrative;
        p.fields.push(['Basis', 'A judgement in a design fixture: ' + WB.moduleName(WB.citeModule(table.owner)), false]);
      }
      if (o.kind === 'calculated' && o.scale) p.note = 'Set by a deterministic rule (interfaces §7 for Portfolio Fit; covenant and gate rules for tests), not by a judgement.';
      if (o.kind === 'none' && o.register) p.note = 'A register row from the host. This table carries no citation column.';
      if (o.kind === 'none' && info && !info.cites.length) p.note = 'The row’s cite column is empty, so no source is stated for this value.';
      if (o.kind === 'none') {
        // a figure with no source stated: the passport says so, and names the row it sits in
        p.fields.push(['Source', 'No source stated by the module', false]);
        const around = WB.rowContextText(table, d.r, d.c);
        if (around) p.fields.push(['In the row', around, false]);
      }
      return p;
    }
    if (d.t === 'row') {
      const table = WB.table(d.table);
      if (!table) return Object.assign(P0, { title: 'Table ' + d.table + ' is not in this run' });
      const info = WB.rowInfo(table, d.r);
      const kinds = WB.columnKinds(table);
      const label = WB.rowLabel(table, d.r);
      const p = Object.assign(P0, { code: '', id: d.table + ' · row ' + (d.r + 1), title: label || 'Row ' + (d.r + 1), sub: 'Row ' + (d.r + 1) + ' \u00B7 ' + WB.tableWhere(table), table: { id: d.table, row: d.r, col: -1 } });
      if (!info) {
        p.note = 'This table carries no citation column.';
        return p;
      }
      p.cites = info.citations.map(citeChip);
      const first = (info.synthetic ? info.citations.find((c) => !c.missing && c.synthetic) : info.citations.find((c) => !c.missing && !c.synthetic)) || info.citations.find((c) => !c.missing);
      if (info.calc) {
        p.kind = 'calculated';
        p.formula = info.calc;
        p.note = ORIGIN_NOTE.calculated;
        for (const c of info.citations) if (!c.missing) p.inputs.push({ id: c.id, label: (c.source || '') + (c.locator ? ' \u00B7 ' + c.locator : ''), desc: { t: 'cite', module: c.module, id: c.id } });
      } else if (info.cites.length) {
        p.kind = info.synthetic ? 'synthetic' : 'cited';
        p.note = ORIGIN_NOTE[p.kind];
        if (first) {
          p.excerpt = first.excerpt;
          p.fields.push(['File', first.source, true], ['Locator', first.locator, true]);
          p.usedIn = WB.citationUses(first.module, first.id).length;
        }
      } else p.note = 'The row\u2019s cite column is empty, so no source is stated for this row.';
      if (info.note) p.fields.push(['Note in cite column', info.note, false]);
      return p;
    }
    if (d.t === 'mcell') {
      const line = WB.modelLine(d.lineId);
      const cell = WB.modelCell(d.lineId, d.columnId);
      const col = ((WB.run.model && WB.run.model.columns) || []).find((x) => x.column_id === d.columnId);
      if (!line || !cell) return Object.assign(P0, { title: 'Model cell not found', note: d.lineId + ' / ' + d.columnId });
      const p = Object.assign(P0, {
        kind: cell.value != null ? (cell.basis === 'REPORTED' ? ((cell.sources || []).some((x) => (WB.citation(x.module, x.citation_id) || {}).synthetic) ? 'synthetic' : 'cited') : 'calculated') : 'gap',
        code: '',
        id: line.line_id + ' \u00B7 ' + d.columnId,
        title: line.label,
        sub: 'Model · band ' + line.band + ' · ' + (col ? col.label : d.columnId),
        fields: [],
        note: '',
      });
      if (cell.value != null) {
        p.fields.push(['Served as', WB.groupServed(cell.value), true], ['Basis', cell.basis || '', false], ['Unit', line.unit_label || line.unit || '', false]);
        if (line.formula) p.formula = line.formula;
        const srcChips = (cell.sources || []).map((x) => ({ id: x.citation_id, module: x.module, label: x.source + ' · ' + x.locator, synthetic: !!(WB.citation(x.module, x.citation_id) || {}).synthetic, desc: { t: 'cite', module: x.module, id: x.citation_id } }));
        if (p.kind === 'calculated') p.inputs = srcChips;
        else p.cites = srcChips;
        if (cell.sources && cell.sources[0]) p.excerpt = cell.sources[0].excerpt;
        if (cell.note) p.note = cell.note;
        if (cell.basis === 'PROJECTED') p.note = 'Projected by the Model from the rate deck and drivers. ' + (p.note || '');
      } else {
        p.fields.push(['Missing', line.label + ' in ' + (col ? col.label : d.columnId), false], ['Reason', (WB.REASONS[cell.reason] || cell.reason) + ' (' + cell.reason + ')', false]);
        p.note = ORIGIN_NOTE.gap;
      }
      return p;
    }
    if (d.t === 'gap') {
      const items = d.items || WB.gapsByIds(d.ids || []);
      return Object.assign(P0, {
        kind: 'gap',
        code: (d.ids || []).join(' '),
        title: items.length ? items[0].missing : 'Gap ' + (d.ids || []).join(' '),
        sub: items.length ? WB.moduleName(items[0].module) : '',
        fields: items.length ? [['Reason', items[0].text, false]] : [['Reason', 'No gap text for this id in the run.', false]],
        gaps: items,
        note: ORIGIN_NOTE.gap,
      });
    }
    if (d.t === 'note') {
      return Object.assign(P0, { kind: d.kind || 'none', code: d.code || '', title: d.title || '', sub: d.sub || '', fields: d.fields || [], note: d.note || ORIGIN_NOTE[d.kind] || '', excerpt: d.excerpt || null, cites: d.cites || [], gapChips: d.gapChips || [], table: d.table || null });
    }
    if (d.t === 'chart') {
      const ch = (WB.run.charts || []).find((x) => x.chart_id === d.chartId);
      if (!ch) return Object.assign(P0, { title: 'Chart ' + d.chartId + ' is not in this run' });
      return Object.assign(P0, {
        kind: ch.origin === 'host' ? 'calculated' : 'model',
        code: '',
        id: ch.chart_id + ' · ' + ch.kind + ' · ' + ch.where,
        title: WB.chartTitle(ch.chart_id),
        sub: 'From ' + (ch.tables || []).map((t) => WB.tableTitle(t)).join(', '),
        fields: [['Origin', ch.origin === 'host' ? 'Host-computed from the Model, Fit or a recomputed module table' : 'Model-authored figures from the module tables', false]],
        chart: ch.chart_id,
        note: '',
      });
    }
    return Object.assign(P0, { title: 'Unknown passport type ' + d.t });
  };

  /* Page state shared by views, the navigator and the inspector */
  WB.page = { outline: [], gapModules: [], title: '' };
  WB.setOutline = (items) => {
    WB.page.outline = items || [];
  };
  WB.state = { honest: false, navFilter: 'all', collapsed: false };

  /* routing helpers */
  WB.href = function (view, anchor, runId) {
    const run = runId || (WB.run && WB.run._id) || WB.runIds[0];
    return '#/' + run + '/' + view + (anchor ? '/' + anchor : '');
  };
  WB.DEFAULT_RUN = 'czr-full-credit-assessment';
})();
