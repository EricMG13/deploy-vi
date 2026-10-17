/* WB Front Pages B: Covenant & Refinancing, Distressed & Restructuring, Portfolio Decision.
   Each page is a composition of panels built from the run's tables and charts (front_page_blocks, handoff tables, charts whose
   `where` is front_page:<block>). Nothing is typed in: every figure is a WB.fig / renderCell bound to a table cell. A block the run
   did not show is a condition line. Registered through WB.registerFrontPage. */
(function () {
  'use strict';
  const WB = window.WB;
  const el = WB.el;

  /* ---------- data access ---------- */
  const T = (id) => WB.table(id);
  const ci = (t, n) => t.columns.indexOf(n);
  const V = (t, r, n) => (r < 0 || ci(t, n) < 0 ? '' : t.rows[r][ci(t, n)]);
  const rowsWhere = (t, pred) => (t ? t.rows.map((x, i) => i).filter((i) => pred(t.rows[i], i)) : []);
  const uniq = (a) => Array.from(new Set(a));
  const digit = (v) => {
    const m = /^V?(\d)/.exec(String(v));
    return m ? +m[1] : 99;
  };
  const cellDesc = (t, r, n) => ({ t: 'cell', table: t.id, r, c: ci(t, n) });
  const mod = (t) => WB.citeModule(t.owner);
  const inl = (text, t) => WB.inline(String(text), t ? mod(t) : undefined);

  /* a figure bound to one table cell; an n/a cell gives its gap chip */
  function fig(t, r, n, text, extra) {
    const c = ci(t, n);
    const o = WB.cellOrigin(t, r, c);
    if (o.kind === 'gap') return WB.renderCell(t, r, c).node;
    const shown = text == null ? WB.fmtNum(t.rows[r][c], { group: WB.columnKinds(t)[c].kind === 'numeric' }) : text;
    return WB.fig(cellDesc(t, r, n), shown, { kind: o.kind, label: WB.figLabel(shown, o.kind, extra) });
  }
  const cellNode = (t, r, n) => WB.renderCell(t, r, ci(t, n)).node;
  const unitSuffix = (u) => {
    const s = String(u || '').trim();
    if (s === 'x' || s === '%') return s;
    if (/^(US\$ ?m|USD millions)$/i.test(s)) return ' US$ m';
    return s ? ' ' + s : '';
  };
  const money = (t, r, n, unitCol) => {
    const u = String(V(t, r, unitCol || 'unit_label'));
    const v = WB.fmtNum(V(t, r, n));
    if (/^(US\$ ?m|USD millions)$/i.test(u)) return 'US$' + v + 'm';
    if (/month/i.test(u)) return v + ' months';
    return v + unitSuffix(u);
  };

  /* ---------- panels ---------- */
  const tagsOf = (tables) => {
    const tags = [];
    tables.forEach((t) => t && WB.tableTags(t).forEach((x) => !tags.find((y) => y.kind === x.kind) && tags.push(x)));
    return tags;
  };
  function P(o) {
    const tables = (o.tables || []).map(T).filter(Boolean);
    const owner = o.owner || (tables[0] && tables[0].owner) || null;
    const blocked = owner && owner !== 'RUN_BRIEF' && WB.stepStatus(owner) === 'blocked';
    const href = owner && WB.ownerHref(owner);
    const anchor = o.linkAnchor || (tables[0] ? 't-' + WB.cssId(tables[0].id) : null);
    return WB.panel({
      title: o.title,
      code: owner === 'RUN_BRIEF' ? 'BRIEF' : owner,
      anchor: o.anchor,
      tags: (o.tags || tagsOf(tables)).filter((x) => o.keepModel || x.kind !== 'model'),
      state: blocked ? { word: 'Blocked', tone: 'neg', icon: 'status-blocked' } : null,
      note: o.note,
      link: href && o.link !== false ? { href: href + (anchor ? '/' + anchor : ''), label: 'Full analysis' } : null,
      body: o.body,
      collapsed: o.collapsed,
      className: o.className,
    });
  }
  function condPanel(title, owner, text, anchor) {
    return WB.panel({ title, code: owner, anchor, collapsible: false, className: 'panel-cond', note: text, body: null });
  }
  const pad = (kids, cls) => el('div', { class: 'pad ' + (cls || '') }, kids);
  const split = (l, r, cls) => el('div', { class: 'fb-split ' + (cls || '') }, [el('div', { class: 'fb-l' }, l), el('div', { class: 'fb-r' }, r)]);
  const subh = (text) => el('h3', { class: 'sub-h' }, text);
  const note = (kids) => el('p', { class: 'fb-note' }, kids);

  /* one chart by id; the panel or a sub-heading names it, so its caption is for assistive technology (never the fixture's summary) */
  function chartNode(id, o) {
    const opts = o || {};
    const c = (WB.run.charts || []).find((x) => x.chart_id === id);
    if (!c) return WB.conditionLine('The chart "' + WB.chartTitle(id) + '" is not in this run.');
    return WB.chartSlot(c, Object.assign({ caption: opts.caption === true, summary: opts.summary || '' }, opts.slot || {}));
  }
  /* money in the house style: US$5,000,000 and US$491.6m (the currency before the figure, the scale after it) */
  function cash(cur, v) {
    const m = /^(US\$|€|£)\s?(m|bn|k)?$/.exec(String(cur || '').trim());
    const n = WB.fmtNum(v, { group: true });
    return m ? m[1] + n + (m[2] || '') : (cur ? cur + ' ' : '') + n;
  }
  /* a bare amount in a sentence about a money table gets its unit: "the 50 covenant floor" reads "the US$50m covenant floor" */
  function withMoneyUnit(text, unitLabel) {
    if (!/^(US\$ ?m|USD millions)$/i.test(String(unitLabel || ''))) return String(text);
    return String(text).replace(/\b(the |a )(\d[\d,.]*) (covenant|liquidity|minimum) floor\b/g, (m0, art, n, w) => art + 'US$' + n + 'm ' + w + ' floor');
  }

  /* a table built from cells already rendered: first column is the row header */
  function gridTable(heads, rows, o) {
    const opts = o || {};
    const tbl = el('table', { class: 'dt fb-t' + (opts.cls ? ' ' + opts.cls : ''), 'data-grid': '1' }, [
      el('caption', { class: 'sr-only' }, opts.caption || 'Table'),
      el('thead', null, el('tr', null, heads.map((h, i) => el('th', { scope: 'col', class: 'h-' + (h.kind || 'text') + (h.cls ? ' ' + h.cls : '') }, h.label)))),
      el('tbody', null, rows.map((r) => el('tr', { class: r.cls || false }, r.cells.map((c, i) => el(i === 0 ? 'th' : 'td', { class: (c.cls || '') + (i === 0 ? ' c-rowh' : ''), scope: i === 0 ? 'row' : false }, c.node))))),
    ]);
    WB.initGrid(tbl);
    return el('div', { class: 'tw' }, tbl);
  }
  const label = (t, n) => WB.columnKinds(t)[ci(t, n)].label;
  /* a table of chosen columns over chosen rows; cells from renderCell so every figure keeps its passport */
  function miniTable(t, rows, cols, o) {
    const opts = o || {};
    const heads = cols.map((n) => ({ label: (opts.labels && opts.labels[n]) || label(t, n), kind: WB.columnKinds(t)[ci(t, n)].kind }));
    const body = rows.map((r) => ({
      cls: opts.rowCls ? opts.rowCls(r) : false,
      cells: cols.map((n, k) => {
        const c = WB.renderCell(t, r, ci(t, n));
        if (k === 0 && opts.sub) return { cls: c.cls, node: el('span', { class: 'fb-cellsub' }, [c.node, opts.sub(r)]) };
        return c;
      }),
    }));
    return gridTable(heads, body, { caption: opts.caption || WB.tableTitle(t.id), cls: opts.cls });
  }
  const tableOrCond = (id, make) => {
    const t = T(id);
    if (!t) return WB.conditionLine('The table ' + id + ' is not in this run.');
    if (!t.rows.length) return WB.conditionLine('The table ' + WB.tableTitle(id) + ' has no rows in this run.');
    return make(t);
  };

  /* ---------- the verdict bar ---------- */
  const QUESTIONS = {
    covenant_refinancing: 'Which provisions protect creditors, and can the issuer refinance?',
    distressed_restructuring: 'Is the distress gate met, which path and fulcrum are most credible, and what recoveries follow?',
    portfolio_decision: 'Should each portfolio own it, how much, and which instrument?',
  };
  function bar(run, tools, o) {
    const cfg = WB.callConfig(run);
    const meta = cfg.meta;
    return WB.verdictBar({
      title: o.title,
      question: QUESTIONS[run.front_page],
      illustrative: true,
      meta,
      notices: o.notices || [],
      tiles: o.tiles || cfg.tiles,
      lines: o.lines || cfg.lines,
      honest: WB.state.honest ? o.honest : null,
      tools: el('span', { class: 'v-tools' }, tools),
      maxLines: WB.CALL_MAX[run.front_page] || 3,
      order: WB.CALL_ORDER[run.front_page] || [],
    });
  }

  /* ---------- shared call-line pieces ---------- */
  const RW = (t, re) => rowsWhere(t, (x) => re.test(String(x[ci(t, 'item')])))[0];
  function runwayLine(run) {
    const t = T('cp2d.runway');
    if (!t || !t.rows.length) return { label: 'LIQUIDITY', tone: 'neu', children: 'No liquidity runway in this run.' };
    const acc = RW(t, /^Accessible liquidity/);
    const use = RW(t, /^Mandatory uses/);
    const head = RW(t, /^Headroom/);
    const mo = RW(t, /^Months/);
    const pinch = RW(t, /^Pinch/);
    const kids = [];
    const hv = head == null ? null : parseFloat(String(V(t, head, 'value')).replace(/[(),\s]/g, '').replace(/^−/, '-'));
    if (acc != null) kids.push(fig(t, acc, 'value', money(t, acc, 'value')), ' accessible against mandatory uses of ', use != null ? fig(t, use, 'value', money(t, use, 'value')) : 'n/a', ' over 12 months');
    if (mo != null) kids.push(': ', fig(t, mo, 'value', money(t, mo, 'value')), ' of runway');
    if (head != null) kids.push(', headroom ', fig(t, head, 'value', money(t, head, 'value')));
    kids.push('. ');
    const unitOf = acc != null ? V(t, acc, 'unit_label') : '';
    if (pinch != null) kids.push(el('b', null, 'Pinch point '), WB.inline(withMoneyUnit(V(t, pinch, 'value'), unitOf), mod(t)));
    const tone = hv != null && hv < 0 ? 'neg' : 'neu';
    return { label: 'LIQUIDITY', tone, children: kids };
  }

  /* ---------- covenant tests: chart beside a compact table ---------- */
  const isProForma = (t, r) => /pro forma/i.test(String(V(t, r, 'test')));
  function covTable(t) {
    const heads = [{ label: 'Test' }, { label: 'Thr.', cls: 'h-numeric' }, { label: 'Cur.', cls: 'h-numeric' }, { label: 'Head.', cls: 'h-numeric' }, { label: 'Status' }];
    const rows = t.rows.map((x, r) => {
      const suf = unitSuffix(V(t, r, 'unit_label'));
      const num = (n) => ({ cls: 'c-num', node: fig(t, r, n, WB.fmtNum(V(t, r, n)) + (suf === ' US$ m' ? '' : suf)) });
      const full = String(V(t, r, 'test'));
      const short = full.replace(/\s*\(.*?\)\s*/g, ' ').trim();
      return {
        cls: isProForma(t, r) ? 'fb-pf' : false,
        cells: [{ cls: 'c-text', node: el('span', { class: 'fb-cellsub' }, [el('span', { class: 'fb-tn', title: full }, short), el('span', { class: 'fb-sub' }, [V(t, r, 'test_type'), V(t, r, 'direction'), suf === ' US$ m' ? 'US$ m' : null].filter(Boolean).join(' · '))]) }, num('threshold'), num('current_value'), num('headroom'), WB.renderCell(t, r, ci(t, 'status'))],
      };
    });
    return gridTable(heads, rows, { caption: WB.tableTitle(t.id), cls: 'fb-cov' });
  }
  function covenantBody(run, withNotes) {
    const t = T('cp4.covenant_tests');
    if (!t || !t.rows.length) return pad(WB.conditionLine('No covenant tests in this run.'));
    const kids = [split(chartNode('chart.covenant_headroom'), covTable(t), 'fb-cov-split')];
    if (withNotes) {
      const rf = T('cp4.red_flags');
      const sp = rf ? rowsWhere(rf, (x) => /spring/i.test(String(x[ci(rf, 'flag')])))[0] : null;
      const parts = [];
      const end = (x) => String(x).replace(/\s*$/, '').replace(/([^.!?])$/, '$1.');
      if (sp != null) parts.push(el('b', null, end(V(rf, sp, 'flag'))), ' ', WB.inline(end(V(rf, sp, 'creditor_risk')), mod(rf)), ' ');
      const ids = uniq(String(V(t, 0, 'basis')).match(/\bG\d+\b/g) || []);
      if (ids.length) parts.push(WB.inline('Ratios are on RBOT’s basis (' + ids.join(', ') + ').', mod(t)));
      if (parts.length) kids.push(note(parts));
    }
    return el('div', { class: 'fb-pbody' }, kids);
  }

  /* ---------- liquidity runway: waterfall beside the runway rows ---------- */
  function runwayTable(t) {
    const rows = [];
    t.rows.forEach((x, r) => {
      if (/^Pinch/.test(String(V(t, r, 'item')))) return;
      const u = String(V(t, r, 'unit_label'));
      const text = WB.fmtNum(V(t, r, 'value')) + (/month/i.test(u) ? '' : '');
      rows.push({ cells: [{ cls: 'c-text', node: el('span', { class: 'fb-cellsub' }, [WB.renderCell(t, r, ci(t, 'item')).node, el('span', { class: 'fb-sub' }, /month/i.test(u) ? 'months' : /US\$ ?m|USD millions/i.test(u) ? 'US$ m' : u)]) }, { cls: 'c-num', node: fig(t, r, 'value', text) }] });
    });
    return gridTable([{ label: 'Runway' }, { label: 'Value', cls: 'h-numeric' }], rows, { caption: WB.tableTitle(t.id), cls: 'fb-run' });
  }
  function liquidityBody() {
    const t = T('cp2d.runway');
    const kids = [split(chartNode('chart.liquidity_bridge'), t && t.rows.length ? runwayTable(t) : WB.conditionLine('No runway table in this run.'), 'fb-run-split')];
    if (t) {
      const p = RW(t, /^Pinch/);
      const acc = RW(t, /^Accessible liquidity/);
      if (p != null) {
        // two sentences: the pinch point, then how it is found
        const val = withMoneyUnit(V(t, p, 'value'), acc != null ? V(t, acc, 'unit_label') : '').replace(/\s*$/, '');
        kids.push(note([el('b', null, 'Pinch point '), inl(/[.!?]$/.test(val) ? val : val + '.', t), ' ', cellNode(t, p, 'basis'), /[.!?]$/.test(String(V(t, p, 'basis'))) ? '' : '.']));
      }
    }
    return el('div', { class: 'fb-pbody' }, kids);
  }
  function liquiditySourcesPanel(collapsed) {
    const s = T('cp2d.liquidity_sources');
    const u = T('cp2d.cash_uses_12m');
    const col = (id, tid, title) => el('div', { class: 'fb-col' }, [subh(title), chartNode(id), tableOrCond(tid, (t) => WB.renderTable(t, { maxRows: 12 }))]);
    return P({ title: 'Liquidity sources and uses', anchor: 'liquidity-sources', tables: ['cp2d.liquidity_sources', 'cp2d.cash_uses_12m'], collapsed, note: s && u ? s.rows.length + ' sources, ' + u.rows.length + ' uses in the next 12 months' : null, body: pad([el('div', { class: 'fb-2col' }, [col('chart.liquidity_sources', 'cp2d.liquidity_sources', 'Sources'), col('chart.cash_uses', 'cp2d.cash_uses_12m', 'Uses')])]) });
  }

  /* ---------- maturity wall and capital structure ---------- */
  function maturityPanel() {
    const tot = T('snapshot.capital_structure_totals');
    const right = tot && tot.rows.length ? miniTable(tot, tot.rows.map((x, i) => i), ['line', 'amount', 'ssim_multiple_x', 'pct_ev_pct'], { labels: { ssim_multiple_x: 'x EBITDA', pct_ev_pct: '% EV' }, cls: 'fb-capt' }) : WB.conditionLine('No capital structure summary in this run.');
    return P({ title: 'Maturity wall and capital structure', anchor: 'maturity-wall', tables: ['model.maturity_wall', 'snapshot.capital_structure_totals'], linkAnchor: 'c-chart-maturity_wall', body: split(chartNode('chart.maturity_wall'), el('div', null, [el('h3', { class: 'sub-h fb-sub-h' }, 'Capital structure summary'), right]), 'fb-wall-split') });
  }
  function capstructPanel(collapsed) {
    return P({ title: 'Capital structure by facility', anchor: 'capital-structure', tables: ['snapshot.capital_structure'], collapsed, body: tableOrCond('snapshot.capital_structure', (t) => WB.renderTable(t, { hide: ['bloomberg_id', 'column_basis'], maxRows: 20 })) });
  }

  /* ---------- funding gap ---------- */
  function fundingPanel(extraTables) {
    const t = T('cp3c.maturity_pressure');
    return P({ title: 'Funding gap', anchor: 'funding-gap', tables: ['cp3c.maturity_pressure'], note: 'before operating cash flow', body: split(chartNode('chart.funding_gap'), t && t.rows.length ? miniTable(t, t.rows.map((x, i) => i), ['fiscal_year', 'maturing_amount', 'sources_available', 'funding_gap', 'pressure'], { labels: { fiscal_year: 'Year', maturing_amount: 'Maturing', sources_available: 'Sources', funding_gap: 'Gap' }, cls: 'fb-gapt' }) : WB.conditionLine('No maturity pressure table in this run.'), 'fb-gap-split') });
  }

  /* ---------- red flags, protection score, refinancing paths, capacity, LME ---------- */
  function flagList(t, compact) {
    const ul = el('ul', { class: 'fb-flags' });
    t.rows.forEach((x, r) => {
      const flag = String(V(t, r, 'flag'));
      const prot = /protective/i.test(flag);
      ul.appendChild(
        el('li', { class: 'fb-flag' }, [
          el('span', { class: 'fb-sev' }, cellNode(t, r, 'severity')),
          el('div', { class: 'fb-ft' }, [el('div', { class: 'fb-fn' }, [cellNode(t, r, 'flag'), prot ? el('span', { class: 'fb-prot' }, [WB.icon('lock', { size: 11, stroke: 1.8 }), 'Protective']) : null]), compact ? null : el('div', { class: 'fb-fp' }, cellNode(t, r, 'provision'))]),
        ])
      );
    });
    return ul;
  }
  function redFlagsPanel(compact) {
    return P({ title: 'Red flags', anchor: 'red-flags', tables: ['cp4.red_flags'], body: tableOrCond('cp4.red_flags', (t) => flagList(t, compact)) });
  }
  function protectionPanel() {
    return P({
      title: 'Lender protection score',
      anchor: 'protection',
      tables: ['cp4.protection_score'],
      body: tableOrCond('cp4.protection_score', (t) => {
        const rows = t.rows.map((x, r) => {
          const v = +V(t, r, 'score');
          const tone = v <= 2 ? 'neg' : v === 3 ? 'cau' : 'pos';
          const o = WB.cellOrigin(t, r, ci(t, 'score'));
          const bars = el('span', { class: 'fb-bars tone-' + tone, 'aria-hidden': 'true' }, [1, 2, 3, 4, 5].map((i) => el('span', { class: i <= v ? 'on' : '' })));
          const sc = el('span', { class: 'fb-score' }, [bars, WB.fig(cellDesc(t, r, 'score'), v + ' of 5', { kind: o.kind, label: WB.figLabel(v + ' of 5', o.kind) })]);
          return { cls: /^Overall/i.test(String(V(t, r, 'area'))) ? 'fb-total' : false, cells: [{ cls: 'c-text', node: cellNode(t, r, 'area') }, { cls: 'c-scale', node: sc }, { cls: 'c-prose', node: cellNode(t, r, 'evidence') }] };
        });
        return gridTable([{ label: 'Area' }, { label: 'Score' }, { label: 'Evidence' }], rows, { caption: WB.tableTitle(t.id), cls: 'fb-prot-t' });
      }),
    });
  }
  function refiPanel(extra) {
    return P({
      title: 'Refinancing paths',
      anchor: 'refi-paths',
      tables: ['cp3c.refinancing_paths'],
      body: tableOrCond('cp3c.refinancing_paths', (t) => miniTable(t, t.rows.map((x, i) => i), ['path', 'feasibility', 'creditor_impact'], { cls: 'fb-refi' })),
    });
  }
  function capacityPanel(collapsed) {
    const t = T('cp4.capacity_register');
    const parts = [];
    let shown = 0;
    if (t) {
      t.rows.forEach((x, r) => {
        const rem = String(V(t, r, 'remaining'));
        if (WB.isNumeric(rem) && shown < 2) {
          shown++;
          parts.push((parts.length ? '; ' : '') + String(V(t, r, 'basket')) + ': ', fig(t, r, 'remaining', WB.fmtNum(rem)), ' remaining');
        }
      });
      const nc = rowsWhere(t, (x) => /not computable|not stated/i.test(String(x[ci(t, 'remaining')]) + String(x[ci(t, 'used')]))).length;
      if (nc) parts.push((parts.length ? '; ' : '') + nc + ' baskets with usage not computable');
    }
    return P({
      title: 'Capacity',
      anchor: 'capacity',
      tables: ['cp4.capacity_register'],
      collapsed,
      note: parts.length ? el('span', null, parts) : null,
      body: pad([split(chartNode('chart.basket_capacity'), tableOrCond('cp4.capacity_register', (tt) => WB.renderTable(tt, { hide: ['formula', 'risk_mechanism', 'credit_implication'], maxRows: 10 })), 'fb-cap-split')]),
    });
  }
  function lmePanel(collapsed) {
    const ce = T('cp3c.creditor_exposure');
    const parts = [];
    if (ce) {
      const base = rowsWhere(ce, (x) => /unsecured/i.test(x[ci(ce, 'creditor_class')]) && x[ci(ce, 'case_name')] === 'Base')[0];
      const lme = rowsWhere(ce, (x) => /unsecured/i.test(x[ci(ce, 'creditor_class')]) && x[ci(ce, 'case_name')] === 'LME')[0];
      if (base != null && lme != null) parts.push('Claims at or ahead of the unsecured notes ', fig(ce, base, 'exposure'), ' Base, ', fig(ce, lme, 'exposure'), ' LME');
    }
    return P({
      title: 'LME capacity and creditor exposure',
      anchor: 'lme',
      tables: ['cp3c.lme_capacity', 'cp3c.creditor_exposure'],
      collapsed,
      note: parts.length ? el('span', null, parts) : null,
      body: pad([
        subh('LME capacity'),
        tableOrCond('cp3c.lme_capacity', (t) => WB.renderTable(t, { hide: ['evidence'], maxRows: 10 })),
        subh('Creditor exposure'),
        split(chartNode('chart.lme_exposure'), tableOrCond('cp3c.creditor_exposure', (t) => WB.renderTable(t, { maxRows: 10 })), 'fb-lme-split'),
      ]),
    });
  }
  function ebitdaPanel(collapsed) {
    return P({ title: 'EBITDA definition', anchor: 'ebitda-def', tables: ['cp4.ebitda_definition'], collapsed, note: 'Cited clauses and their capacity effect', body: tableOrCond('cp4.ebitda_definition', (t) => WB.renderTable(t, { maxRows: 10 })) });
  }
  function docsPanel(collapsed) {
    const d = T('cp4.document_register');
    const s = T('cp4.structure_map');
    return P({ title: 'Document register and structure map', anchor: 'documents', tables: ['cp4.document_register', 'cp4.structure_map'], collapsed, note: d && s ? d.rows.length + ' documents, ' + s.rows.length + ' entities' : null, body: pad([subh('Document register'), tableOrCond('cp4.document_register', (t) => WB.renderTable(t, { maxRows: 12 })), subh('Structure map'), tableOrCond('cp4.structure_map', (t) => WB.renderTable(t, { maxRows: 12 }))]) });
  }

  /* ---------- credit view and new tranches ---------- */
  function creditViewPanel(collapsed) {
    const cv = T('snapshot.credit_view');
    return P({
      title: 'Credit view',
      anchor: 'credit-view',
      tables: ['snapshot.credit_view'],
      collapsed,
      body: tableOrCond('snapshot.credit_view', (t) => {
        const strip = el('div', { class: 'fb-cv' }, ['credit_score', 'credit_direction', 'sector_outlook', 'confidence'].filter((n) => ci(t, n) >= 0).map((n) => el('div', { class: 'fb-cvi' }, [el('span', { class: 'fb-cvl' }, label(t, n)), cellNode(t, 0, n)])));
        const txt = ['primary_support', 'primary_downside'].filter((n) => ci(t, n) >= 0).map((n) => el('div', { class: 'fb-cvt' }, [el('span', { class: 'fb-cvl' }, label(t, n)), el('p', null, cellNode(t, 0, n))]));
        return pad([strip, el('div', { class: 'fb-cv-txt' }, txt)]);
      }),
    });
  }
  function tranchesPanel(collapsed) {
    const t = T('snapshot.transaction_summary');
    return P({ title: 'New tranches', anchor: 'tranches', tables: ['snapshot.transaction_summary'], collapsed, note: t ? t.rows.length + ' tranches, CR Score per tranche' : null, body: tableOrCond('snapshot.transaction_summary', (tt) => miniTable(tt, tt.rows.map((x, i) => i), ['instrument', 'debt_type', 'size', 'price_talk', 'expected_ratings', 'cr_score', 'status'])) });
  }
  function tranchesLine() {
    const t = T('snapshot.transaction_summary');
    if (!t || !t.rows.length) return { label: 'NEW TRANCHES', tone: 'neu', children: 'No new tranches in this run.' };
    const kids = [];
    t.rows.forEach((x, r) => {
      if (r) kids.push('; ');
      kids.push(String(V(t, r, 'instrument')), ' ', fig(t, r, 'size', 'US$' + WB.fmtNum(V(t, r, 'size')) + 'm'), ', CR Score ', fig(t, r, 'cr_score'));
    });
    return { label: 'NEW TRANCHES', tone: 'neu', children: kids };
  }

  /* ---------- assembling a page ---------- */
  function notShownPanels(run, used) {
    return (run.front_page_blocks || [])
      .filter((b) => !b.shown && !used.includes(b.id))
      .map((b) => {
        const title = WB.blockTitle(b);
        return { node: condPanel(title, b.id.indexOf('cp8') >= 0 || /what changed/i.test(b.title) ? 'CP-8' : null, b.reason ? 'Not shown: ' + b.reason + '.' : 'Not shown.', b.id), span: 12, label: title, na: true };
      });
  }
  function assemble(canvas, run, o) {
    const root = el('div', { class: 'view view-front view-fpb view-' + run.front_page });
    canvas.appendChild(root);
    root.appendChild(bar(run, WB.collapseTool(() => root), o));
    const grid = el('div', { class: 'fp-grid' });
    const outline = [];
    o.items.concat(notShownPanels(run, o.usedBlocks || [])).forEach((it) => {
      it.node.style.gridColumn = 'span ' + (it.span || 12);
      grid.appendChild(it.node);
      (it.outline || [{ id: it.node.id, label: it.label, na: it.na }]).forEach((x) => outline.push(x));
    });
    root.appendChild(grid);
    WB.setOutline(outline.filter((x) => x.id));
    WB.page.gapModules = uniq(o.items.flatMap((it) => (it.owners || []).map((x) => WB.citeModule(x)))).filter(Boolean);
  }
  const item = (node, label, owners, span) => ({ node, label, owners: owners || [], span: span || 12 });

  /* =================================================================
     COVENANT & REFINANCING
     ================================================================= */
  function covenantPage(canvas, run) {
    const ct = T('cp4.covenant_tests');
    const tiles = WB.callConfig(run).tiles.map((t) => {
      if (t.key === 'status' && ct) {
        const maint = rowsWhere(ct, (x, r) => x[ci(ct, 'test_type')] === 'Maintenance' && !isProForma(ct, r)).length;
        return Object.assign({}, t, { sub: 'Maintenance, ' + maint + ' tests' });
      }
      return t;
    });
    const lines = [];
    if (ct && ct.rows.length) {
      const m = rowsWhere(ct, (x, r) => x[ci(ct, 'test_type')] === 'Maintenance' && !isProForma(ct, r));
      const kids = [];
      m.forEach((r, k) => {
        if (k) kids.push('; ');
        const suf = unitSuffix(V(ct, r, 'unit_label'));
        kids.push(String(V(ct, r, 'test')).replace(/\s*\(.*?\)\s*/g, ''), ' ', fig(ct, r, 'current_value', WB.fmtNum(V(ct, r, 'current_value')) + suf), ' against a ', fig(ct, r, 'threshold', WB.fmtNum(V(ct, r, 'threshold')) + suf), ' ', String(V(ct, r, 'direction')).toLowerCase());
      });
      const paren = m.length ? /\((.*?)\)/.exec(String(V(ct, m[0], 'test'))) : null;
      if (paren) kids.push('; tested for the ', paren[1]);
      kids.push('. ');
      const rf = T('cp4.red_flags');
      const nc = rf ? rowsWhere(rf, (x) => /non-covenant/i.test(String(x[ci(rf, 'flag')])))[0] : null;
      if (nc != null) kids.push(cellNode(rf, nc, 'flag'), '. ');
      const ids = uniq(String(V(ct, 0, 'basis')).match(/\bG\d+\b/g) || []);
      if (ids.length) kids.push(WB.inline('Ratios are on RBOT’s basis (' + ids.join(', ') + ').', mod(ct)));
      // a covenant test that reads Breached makes this a negative call line (it never folds)
      lines.push({ label: 'COVENANTS', tone: ct.rows.some((x, r) => V(ct, r, 'status') === 'Breached') ? 'neg' : 'neu', children: kids });
    } else lines.push({ label: 'COVENANTS', tone: 'neu', children: 'No covenant tests in this run.' });
    lines.push(runwayLine(run));
    lines.push(tranchesLine());
    // the main risk is a call line on every Front Page (content doc 04 states the covenant risk in the credit view's own words)
    const mainRisk = WB.callConfig(run).lines.find((l) => l.label === 'MAIN RISK');
    if (mainRisk) lines.push(mainRisk);
    const plan = run.plan || [];
    const missing = [];
    if (!plan.includes('CP-6')) missing.push('Recommendation');
    if (!plan.includes('CP-3')) missing.push('Valuation');
    if (!plan.includes('FIT')) missing.push('Portfolio Fit');
    const gone = ['CP-3', 'CP-6', 'FIT'].filter((m) => !plan.includes(m)).map((m) => (m === 'FIT' ? 'Fit' : m));
    const chg = (run.front_page_blocks || []).find((b) => !b.shown && /what changed/i.test(b.title));
    // what this Pathway does not run is a notice tag in the byline row (word, icon, module codes); its sentence is the tag's passport
    const absent = [missing.length ? 'No ' + missing.join(', no ').replace(/, no (\w[\w ]*)$/, ' and no $1') + ': this Pathway runs no ' + gone.join(', ').replace(/, ([^,]*)$/, ' or $1') + '.' : '', chg ? 'What changed: not shown' + (chg.reason ? ', ' + chg.reason : '') + '.' : ''].filter(Boolean);
    const notices = absent.length ? [{ word: 'Not in this Pathway', tone: 'neu', icon: 'status-notrun', code: gone.join(' \u00B7 ') || 'What changed', desc: { t: 'note', kind: 'none', code: '', title: 'Not in this Pathway', sub: 'What this Pathway does not produce', fields: absent.map((x, i) => [i ? 'What changed' : 'Reading', x.replace(/^What changed: /, ''), false]), note: 'The page describes protection and refinancing capacity, not whether to own the issuer.' } }] : [];

    const colL = el('div', { class: 'fb-colstack' }, [redFlagsPanel(false)]);
    const colR = el('div', { class: 'fb-colstack' }, [protectionPanel(), refiPanel()]);
    const items = [
      item(P({ title: 'Covenant tests and headroom', anchor: 'covenant-tests', tables: ['cp4.covenant_tests'], body: covenantBody(run, true) }), 'Covenant tests and headroom', ['CP-4']),
      item(P({ title: 'Liquidity runway', anchor: 'runway', tables: ['cp2d.runway'], linkAnchor: 'c-chart-liquidity_bridge', body: liquidityBody() }), 'Liquidity runway', ['CP-2D']),
      item(maturityPanel(), 'Maturity wall', ['MODEL']),
      item(fundingPanel(), 'Funding gap', ['CP-3C']),
    ];
    const cols = el('div', { class: 'fb-cols' }, [colL, colR]);
    items.push({ node: cols, span: 12, owners: ['CP-4', 'CP-3C'], outline: [{ id: 'p-red-flags', label: 'Red flags' }, { id: 'p-protection', label: 'Lender protection score' }, { id: 'p-refi-paths', label: 'Refinancing paths' }] });
    items.push(item(capacityPanel(true), 'Capacity', ['CP-4']));
    items.push(item(lmePanel(true), 'LME capacity and creditor exposure', ['CP-3C']));
    items.push(item(ebitdaPanel(true), 'EBITDA definition', ['CP-4']));
    items.push(item(docsPanel(true), 'Documents and structure', ['CP-4']));
    items.push(item(liquiditySourcesPanel(true), 'Liquidity sources and uses', ['CP-2D']));
    items.push(item(capstructPanel(true), 'Capital structure by facility', ['MODEL']));
    items.push(item(tranchesPanel(true), 'New tranches', ['CP-0']));
    items.push(item(creditViewPanel(true), 'Credit view', ['CP-2']));
    assemble(canvas, run, { title: 'Covenant and refinancing view', tiles, lines, notices, items, honest: 'Honest state: the live CAOS run produced no Credit Score', usedBlocks: [] });
  }

  /* =================================================================
     DISTRESSED & RESTRUCTURING
     ================================================================= */
  function gateStatus() {
    const g = T('cp4c.distress_gate');
    if (!g || !g.rows.length) return null;
    const r = rowsWhere(g, (x) => /^Overall/i.test(String(x[ci(g, 'trigger')])));
    const i = r.length ? r[r.length - 1] : g.rows.length - 1;
    return { t: g, r: i, status: String(V(g, i, 'status')) };
  }
  function gatePanel(gs) {
    const body = tableOrCond('cp4c.distress_gate', (t) => {
      const w = WB.renderTable(t, { maxRows: 12 });
      WB.qsa('tbody tr', w).forEach((tr) => /^Overall/i.test(String(V(t, +tr.dataset.r, 'trigger'))) && tr.classList.add('fb-total'));
      return w;
    });
    const kids = [];
    if (WB.state.honest) kids.push(pad([WB.conditionLine('Honest state: the live CAOS CP-4C run found no named distress trigger and returned Not Applicable, so the gate reads Not met. The triggers below are this fixture’s own.')]));
    kids.push(body);
    return P({ title: 'Distress gate and triggers', anchor: 'distress-gate', tables: ['cp4c.distress_gate'], body: el('div', null, kids) });
  }
  function fulcrumLine(shown) {
    const t = T('cp4c.recoveries');
    if (!shown) return { label: 'FULCRUM', tone: 'neu', children: 'None shown: the distress gate is Not met, so the page runs no recovery scenarios.' };
    if (!t || !t.rows.length) return { label: 'FULCRUM', tone: 'neu', children: 'No recoveries in this run.' };
    const scen = uniq(t.rows.map((x) => x[ci(t, 'scenario')]));
    const kids = [];
    // the fulcrum class by name (the claims register's words), each scenario as "Going concern, low"
    scen.forEach((s, k) => {
      if (k) kids.push('; ');
      const r = rowsWhere(t, (x) => x[ci(t, 'scenario')] === s && x[ci(t, 'fulcrum')] === 'Yes')[0];
      kids.push(el('span', { class: 'fb-scn' }, String(s).replace(/: /, ', ') + ': '));
      if (r == null) kids.push('none');
      else kids.push(el('b', { title: String(V(t, r, 'class_id')) }, WB.claimName(V(t, r, 'class_id'))), ', ', fig(t, r, 'recovery_pct', String(V(t, r, 'recovery_pct')) + ' recovery'));
    });
    return { label: 'FULCRUM', tone: 'neg', children: kids, leadTo: ';' };
  }
  function recoveriesPanels(shown, gs) {
    if (!shown) return [{ node: condPanel('Recoveries', 'CP-4C', 'Not shown: the distress gate is Not met' + (WB.state.honest ? ' (honest state: the live CAOS CP-4C returned Not Applicable).' : '.'), 'recoveries'), label: 'Recoveries', na: true, owners: ['CP-4C'] }];
    const body = el('div', { class: 'fb-pbody' }, [
      note([el('b', null, 'Shown because the distress gate is '), gs ? fig(gs.t, gs.r, 'status') : 'unknown', '. The value of each scenario is allocated to the classes in priority order.']),
      tableOrCond('cp4c.ev_scenarios', (t) => WB.renderTable(t, { maxRows: 8 })),
      subh('Recovery by class'),
      chartNode('chart.recovery_by_class'),
      subh('Value allocation by scenario'),
      chartNode('chart.value_allocation'),
    ]);
    const a = P({ title: 'EV scenarios and recoveries', anchor: 'recoveries', tables: ['cp4c.ev_scenarios', 'cp4c.recoveries'], tags: tagsOf([T('cp4c.recoveries')]), body });
    const b = P({ title: 'Recoveries by class and scenario', anchor: 'recoveries-table', tables: ['cp4c.recoveries'], collapsed: true, body: tableOrCond('cp4c.recoveries', (t) => WB.renderTable(t, { maxRows: 30 })) });
    return [
      { node: a, label: 'EV scenarios and recoveries', owners: ['CP-4C'] },
      { node: b, label: 'Recoveries table', owners: ['CP-4C'] },
    ];
  }
  function ratingPanel() {
    const t = T('cp2h.rating_triggers');
    const kids = [];
    const reason = WB.stepStatus('CP-2H') === 'blocked' ? WB.stepReason('CP-2H') : '';
    kids.push(chartNode('chart.rating_triggers', { caption: false }));
    if (t && t.rows.length) kids.push(subh('Rating triggers'), miniTable(t, t.rows.map((x, i) => i), ['agency', 'rating_type', 'metric', 'threshold', 'current_value', 'status'], { cls: 'fb-rtrig' }));
    const mv = T('cp2h.migration_view');
    if (mv && mv.rows.length) kids.push(subh('Migration view'), miniTable(mv, mv.rows.map((x, i) => i), ['agency', 'case', 'likely_transition', 'earliest_timing', 'confidence'], { cls: 'fb-rtrig' }));
    return P({ title: 'Rating triggers', anchor: 'rating-triggers', tables: ['cp2h.rating_triggers', 'cp2h.migration_view'], note: reason || null, body: el('div', { class: 'fb-pbody fb-pad' }, kids) });
  }
  /* cards: a heading, a badge and labelled prose fields from one row */
  function cards(t, o) {
    return el(
      'div',
      { class: 'fb-cards' },
      t.rows.map((x, r) =>
        el('article', { class: 'fb-card' }, [
          el('header', { class: 'fb-ch' }, [el('h3', null, cellNode(t, r, o.title)), o.badge ? cellNode(t, r, o.badge) : null, o.sub ? el('span', { class: 'fb-csub' }, cellNode(t, r, o.sub)) : null]),
          el('dl', { class: 'fb-dl' }, o.fields.filter((f) => ci(t, f[1]) >= 0).flatMap((f) => [el('dt', null, f[0]), el('dd', null, cellNode(t, r, f[1]))])),
        ])
      )
    );
  }
  function pathsPanel() {
    const kids = [tableOrCond('cp4c.paths', (t) => cards(t, { title: 'path', badge: 'likelihood_class', sub: 'process', fields: [['Consent', 'consent'], ['New money', 'new_money'], ['Class treatment', 'class_treatment'], ['Milestones', 'milestones'], ['Blockers', 'blockers']] }))];
    const rp = T('cp3c.refinancing_paths');
    if (rp) kids.push(subh('Refinancing paths'), miniTable(rp, rp.rows.map((x, i) => i), ['path', 'feasibility', 'creditor_impact'], { cls: 'fb-refi' }));
    return P({ title: 'Restructuring paths', anchor: 'paths', tables: ['cp4c.paths'], body: el('div', { class: 'fb-pbody fb-pad' }, kids) });
  }

  /* instrument decision: levels, valuation, preference and Recommendation per instrument */
  function instrumentDecision(opts) {
    const lv = T('snapshot.instrument_levels');
    const pf = T('cp3.security_preference');
    const rc = T('snapshot.instrument_recommendation');
    const base = rc || lv;
    if (!base) return WB.conditionLine('No instrument table in this run.');
    const ids = uniq((rc ? rc.rows.map((x) => x[ci(rc, 'facility_id')]) : []).concat(lv ? lv.rows.map((x) => x[ci(lv, 'facility_id')]) : []));
    const find = (t, id) => (t ? rowsWhere(t, (x) => x[ci(t, 'facility_id')] === id)[0] : undefined);
    const na = (why) => ({ cls: 'c-gap', node: WB.gapChip([], { label: 'n/a', reason: why }) });
    const pick = (t, id, n, why) => {
      const r = find(t, id);
      return r == null || ci(t, n) < 0 ? na(why) : WB.renderCell(t, r, ci(t, n));
    };
    const rows = ids.map((id) => {
      const r0 = find(rc, id);
      const l0 = find(lv, id);
      const name = r0 != null ? WB.renderCell(rc, r0, ci(rc, 'instrument')) : WB.renderCell(lv, l0, ci(lv, 'instrument'));
      return {
        cells: [
          name,
          pick(lv, id, 'mid', 'No level for this instrument in the run (a quote, mid or talk is not in the Source Pack).'),
          pick(lv, id, 'yield_or_dm', 'No yield or discount margin without a level.'),
          pick(rc, id, 'valuation', 'No Valuation for this instrument.'),
          pick(pf, id, 'preference', 'No preference for this instrument.'),
          pick(rc, id, 'recommendation', 'No Recommendation for this instrument.'),
        ],
      };
    });
    return gridTable([{ label: 'Instrument' }, { label: 'Level (mid)', cls: 'h-numeric' }, { label: 'Yield or DM', cls: 'h-numeric' }, { label: 'Valuation' }, { label: 'Preference' }, { label: 'Recommendation' }], rows, { caption: 'Instrument decision', cls: 'fb-instr' });
  }
  function instrumentPanel() {
    return P({ title: 'Instrument decision', anchor: 'instrument-decision', owner: 'CP-3', tables: ['snapshot.instrument_levels', 'cp3.security_preference', 'snapshot.instrument_recommendation'], linkAnchor: 't-snapshot.instrument_levels', body: instrumentDecision() });
  }

  /* ---------- Portfolio Fit: limits as headroom bars, instruments with verdicts ---------- */
  const NUMLIKE = (s) => /^-?\d+(\.\d+)?$/.test(String(s).replace(/,/g, ''));
  function limitRows(pid) {
    const lt = T('fit.limit_headroom');
    if (!lt) return WB.conditionLine('This run carries no limit headroom table.');
    const seen = new Set();
    const ul = el('ul', { class: 'fb-limits' });
    lt.rows.forEach((x, r) => {
      if (x[ci(lt, 'portfolio_id')] !== pid) return;
      const lid = x[ci(lt, 'limit_id')];
      if (seen.has(lid)) return;
      seen.add(lid);
      const lim = parseFloat(V(lt, r, 'limit_value'));
      const cur = parseFloat(V(lt, r, 'current_value'));
      const status = String(V(lt, r, 'status'));
      const pct = V(lt, r, 'limit_unit') === 'pct_nav';
      const bar = pct && NUMLIKE(V(lt, r, 'current_value')) && NUMLIKE(V(lt, r, 'limit_value'));
      // one rule in every view (WB.limitState): Within with headroom under 10% of the limit reads Tight
      const ls = bar ? WB.limitState(status, lim, cur) : WB.limitState(status);
      const tn = ls.tone;
      const u = pct ? '% NAV' : '';
      const show = (n) => fig(lt, r, n, WB.fmtNum(V(lt, r, n)) + (u && NUMLIKE(V(lt, r, n)) ? '% NAV' : ''));
      const max = Math.max(lim, cur) || 1;
      const pair = (label, n) => el('span', { class: 'fb-lvp' }, [el('span', { class: 'fb-lvl' }, label), show(n)]);
      ul.appendChild(
        el('li', { class: 'fb-lim tone-bg-' + tn }, [
          el('div', { class: 'fb-lh' }, [el('span', { class: 'fb-ln' }, cellNode(lt, r, 'parameter')), el('span', { class: 'fb-lid num' }, lid), el('span', { class: 'fb-lk' }, String(V(lt, r, 'limit_kind')) + ' limit'), el('span', { class: 'fb-ls tone-' + tn }, [WB.icon(ls.icon, { size: 12, stroke: 1.8 }), ls.word])]),
          bar ? el('div', { class: 'fb-lb tone-' + tn, role: 'img', 'aria-label': 'Current ' + cur + ' of a ' + lim + ' limit, ' + ls.word }, [el('span', { class: 'fb-lf', style: { width: (Math.max(0, cur) / max) * 100 + '%' } }), el('span', { class: 'fb-lt', style: { left: (lim / max) * 100 + '%' } })]) : null,
          el('div', { class: 'fb-lv' }, [pair('Limit', 'limit_value'), pair('Current', 'current_value'), pair('Headroom', 'headroom')]),
        ])
      );
    });
    return seen.size ? ul : WB.conditionLine('No limits are recorded for this portfolio.');
  }
  function fitInstruments(pid) {
    const pf = T('snapshot.portfolio_fit');
    if (!pf) return WB.conditionLine('This run carries no Portfolio Fit table.');
    const rows = rowsWhere(pf, (x) => x[ci(pf, 'portfolio_id')] === pid);
    const heads = [{ label: 'Instrument' }, { label: 'Max size', cls: 'h-numeric' }, { label: 'Binding limit' }, { label: 'Verdict' }, { label: 'Caps at' }];
    // the unit sits in the head ("Max size, US$" or "Max size, US$ m"): a bare currency never trails a figure
    const units = uniq(rows.map((r) => WB.unitLabel(V(pf, r, 'currency'), V(pf, r, 'unit'))));
    if (units.length === 1 && units[0]) heads[1] = { label: 'Max size, ' + units[0], cls: 'h-numeric' };
    const body = rows.map((r) => {
      const u = WB.unitLabel(V(pf, r, 'currency'), V(pf, r, 'unit'));
      const mc = WB.renderCell(pf, r, ci(pf, 'max_size'));
      const bad = V(pf, r, 'verdict') === 'Breaches';
      return {
        cls: bad ? 'fb-breach' : false,
        cells: [WB.renderCell(pf, r, ci(pf, 'instrument')), { cls: mc.cls, node: units.length === 1 ? mc.node : el('span', { class: 'fb-ms' }, [mc.node, el('span', { class: 'fb-u' }, u)]) }, WB.renderCell(pf, r, ci(pf, 'binding_limit')), WB.renderCell(pf, r, ci(pf, 'verdict')), WB.renderCell(pf, r, ci(pf, 'recommendation_cap'))],
      };
    });
    return gridTable(heads, body, { caption: 'Instruments against the limits of this portfolio', cls: 'fb-fit' });
  }
  function factFig(label, text, pj, syn) {
    return WB.fig({ t: 'note', kind: syn ? 'synthetic' : 'cited', code: pj.portfolio_id, title: label + ', ' + pj.portfolio_name, sub: 'Portfolio input of the Run Brief', fields: [['Served as', text, true], ['Portfolio', pj.portfolio_name, false], ['As of', WB.fmtDate(pj.as_of), false]], note: syn ? 'TEST DATA: the portfolio input is synthetic. ' + (pj.notes || []).join(' ') : (pj.notes || []).join(' ') }, text, { kind: syn ? 'synthetic' : 'cited', label: label + ': ' + text });
  }
  function fitPanel(f) {
    const pj = f.inputs.portfolio;
    const pid = f.portfolio_id;
    const syn = /synthetic|fictional/i.test((pj.notes || []).join(' ') + ' ' + pj.portfolio_name);
    const pf = T('snapshot.portfolio_fit');
    const rows = pf ? rowsWhere(pf, (x) => x[ci(pf, 'portfolio_id')] === pid) : [];
    const breaches = rows.filter((r) => V(pf, r, 'verdict') === 'Breaches').length;
    const watch = rows.filter((r) => V(pf, r, 'verdict') === 'Watch').length;
    const fits = rows.filter((r) => V(pf, r, 'verdict') === 'Fits').length;
    const cnt = [];
    if (breaches) cnt.push(breaches + ' Breaches');
    if (watch) cnt.push(watch + ' Watch');
    if (fits) cnt.push(fits + ' Fits');
    const cur = WB.unitLabel(pj.currency, pj.unit);
    const facts = [['NAV', cash(cur, pj.nav)], ['Par', cash(cur, pj.par)], ['As of', WB.fmtDate(pj.as_of)], ['Strategy', pj.strategy]];
    const body = [
      el('dl', { class: 'fp-facts fb-facts' }, facts.flatMap((x) => [el('dt', null, x[0]), el('dd', null, x[0] === 'Strategy' ? x[1] : factFig(x[0], x[1], pj, syn))])),
      subh('Limits and headroom'),
      limitRows(pid),
      subh('Instruments'),
      fitInstruments(pid),
    ];
    if ((pj.notes || []).length) body.push(subh('Notes'), el('ul', { class: 'fp-notes fb-notes' }, pj.notes.map((n) => el('li', null, WB.inline(n, 'FIT')))));
    return P({
      title: pj.portfolio_name,
      anchor: 'fit-' + pid,
      owner: 'FIT',
      tables: ['snapshot.portfolio_fit', 'fit.limit_headroom'],
      tags: [{ kind: 'text', label: pj.strategy }].concat(syn ? [{ kind: 'synthetic', label: 'Synthetic' }] : []),
      note: cnt.length ? cnt.join(', ') : null,
      linkAnchor: 'fit-' + pid,
      body: pad(body, 'fb-fitbody'),
    });
  }
  function fitPanels(run) {
    return (run.fit || []).map((f) => ({ node: fitPanel(f), label: 'Fit: ' + f.inputs.portfolio.portfolio_name.replace(/ \(fictional\)/, ''), owners: ['FIT'] }));
  }

  function distressPage(canvas, run) {
    const gs = gateStatus();
    const shown = !(WB.state.honest || (gs && /^not met$/i.test(gs.status)));
    const cfg = WB.callConfig(run);
    const lines = [fulcrumLine(shown)];
    if (gs && WB.state.honest) lines.push({ label: 'GATE', tone: 'pos', children: 'Not met. The live CAOS CP-4C run found no named distress trigger and returned Not Applicable; the fixture\u2019s own triggers are in the gate table below.' });
    else if (gs) {
      const ev = String(V(gs.t, gs.r, 'evidence'));
      lines.push({ label: 'GATE', tone: /^met$/i.test(gs.status) ? 'neg' : /not met/i.test(gs.status) ? 'pos' : 'cau', children: [el('strong', { class: 'v-lead' }, gs.status), '. ', WB.inline(ev, mod(gs.t))] });
    }
    lines.push(runwayLine(run));
    cfg.lines.filter((l) => l.label !== 'FULCRUM').forEach((l) => lines.push(l));

    const items = [];
    const add = (node, label, owners, span) => items.push(item(node, label, owners, span));
    add(gatePanel(gs), 'Distress gate and triggers', ['CP-4C']);
    recoveriesPanels(shown, gs).forEach((x) => items.push(x));
    add(P({ title: 'Claims', anchor: 'claims', tables: ['cp4c.claims_register'], body: tableOrCond('cp4c.claims_register', (t) => WB.renderTable(t, { maxRows: 12 })) }), 'Claims', ['CP-4C']);
    add(P({ title: 'Liquidity runway', anchor: 'runway', tables: ['cp2d.runway'], linkAnchor: 'c-chart-liquidity_bridge', body: liquidityBody() }), 'Liquidity runway', ['CP-2D']);
    add(fundingPanel(), 'Maturity pressure', ['CP-3C']);
    add(lmePanel(false), 'LME capacity and creditor exposure', ['CP-3C']);
    add(P({ title: 'Covenant levers', anchor: 'covenant-levers', tables: ['cp4.covenant_tests', 'cp4.red_flags'], linkAnchor: 't-cp4.covenant_tests', body: el('div', null, [covenantBody(run, false), subh('Red flags'), tableOrCond('cp4.red_flags', (t) => flagList(t, true))]) }), 'Covenant levers', ['CP-4']);
    add(capacityPanel(true), 'Capacity', ['CP-4']);
    add(ratingPanel(), 'Rating triggers', ['CP-2H']);
    add(pathsPanel(), 'Restructuring paths', ['CP-4C', 'CP-3C']);
    add(instrumentPanel(), 'Instrument decision', ['CP-3', 'CP-6']);
    fitPanels(run).forEach((x) => items.push(x));
    if (!(run.fit || []).length) items.push({ node: condPanel('Portfolio Fit', 'FIT', 'Not run: this Pathway attaches no portfolio, so there is no Fit verdict.', 'portfolio-fit'), label: 'Portfolio Fit', na: true });
    add(capstructPanel(true), 'Capital structure by facility', ['MODEL']);
    add(creditViewPanel(true), 'Credit view', ['CP-2']);
    assemble(canvas, run, { title: 'Distress view and recommendation', tiles: cfg.tiles, lines, items, honest: 'Honest state: the live CAOS CP-4C run found no named distress trigger', usedBlocks: [] });
  }

  /* =================================================================
     PORTFOLIO DECISION
     ================================================================= */
  function portfolioRecPanel(run) {
    const pr = T('cp6.portfolio_recommendation');
    const rec = T('snapshot.recommendation');
    const kids = [];
    if (rec && rec.rows.length) kids.push(subh('Recommendation per Strategy'), WB.renderTable(rec, { maxRows: 6 }));
    if (!pr || !pr.rows.length) kids.push(WB.conditionLine('CP-6 did not run in this Pathway, so there is no per-portfolio Recommendation.'));
    else {
      const pt = T('cp0.portfolios');
      const nameOf = (pid) => {
        const f = (run.fit || []).find((x) => x.portfolio_id === pid);
        return (f && f.inputs.portfolio.portfolio_name) || (pt && V(pt, rowsWhere(pt, (x) => x[ci(pt, 'portfolio_id')] === pid)[0], 'portfolio_name')) || pid;
      };
      uniq(pr.rows.map((x) => x[ci(pr, 'portfolio_id')])).forEach((pid) => {
        const rows = rowsWhere(pr, (x) => x[ci(pr, 'portfolio_id')] === pid);
        const syn = (run.fit || []).some((f) => f.portfolio_id === pid && /synthetic|fictional/i.test((f.inputs.portfolio.notes || []).join(' ') + f.inputs.portfolio.portfolio_name));
        kids.push(el('h3', { class: 'sub-h fb-ph' }, [nameOf(pid), ' ', el('span', { class: 'fb-pst' }, V(pr, rows[0], 'strategy')), syn ? WB.tag('synthetic', 'Synthetic') : null]));
        kids.push(miniTable(pr, rows, ['instrument', 'uncapped', 'cap', 'final', 'fit_verdict'], { labels: { fit_verdict: 'Fit verdict' }, rowCls: (r) => (V(pr, r, 'fit_verdict') === 'Breaches' ? 'fb-breach' : false), cls: 'fb-prec', caption: 'Recommendation after the cap, ' + nameOf(pid) }));
      });
      const pairs = uniq(pr.rows.map((x) => x[ci(pr, 'fit_verdict')] + '\u0001' + x[ci(pr, 'cap')]));
      const rule = pairs.map((p) => 'Fit ' + p.split('\u0001')[0] + ' caps at ' + p.split('\u0001')[1]).join('; ');
      kids.push(note([el('b', null, 'Rule. '), rule + '. The final Recommendation is the weaker of the uncapped call and the cap; the cap comes from the verdict of the Portfolio Fit.']));
    }
    return P({ title: 'Portfolio recommendation', anchor: 'portfolio-recommendation', tables: ['cp6.portfolio_recommendation', 'snapshot.recommendation'], linkAnchor: 't-cp6.portfolio_recommendation', owner: 'CP-6', body: el('div', { class: 'fb-pbody fb-pad' }, kids) });
  }
  function capitalPanel() {
    const tot = T('snapshot.capital_structure_totals');
    const right = tot && tot.rows.length ? miniTable(tot, tot.rows.map((x, i) => i), ['line', 'amount', 'ssim_multiple_x', 'pct_ev_pct'], { labels: { ssim_multiple_x: 'x EBITDA', pct_ev_pct: '% EV' }, cls: 'fb-capt' }) : WB.conditionLine('No capital structure summary in this run.');
    return P({ title: 'Capital structure', anchor: 'capital-structure-summary', tables: ['snapshot.capital_structure', 'snapshot.capital_structure_totals'], body: split(chartNode('chart.capital_structure'), right, 'fb-cap2-split') });
  }
  function strengthsPanel() {
    const sw = T('snapshot.strengths_weaknesses');
    const cvT = T('snapshot.credit_view');
    const kids = [];
    if (cvT && cvT.rows.length) kids.push(el('div', { class: 'fb-cv' }, ['credit_score', 'credit_direction', 'sector_outlook', 'confidence'].filter((n) => ci(cvT, n) >= 0).map((n) => el('div', { class: 'fb-cvi' }, [el('span', { class: 'fb-cvl' }, label(cvT, n)), cellNode(cvT, 0, n)]))));
    if (sw && sw.rows.length) {
      const col = (kind, icon, tone) => {
        const rows = rowsWhere(sw, (x) => x[ci(sw, 'kind')] === kind);
        return el('div', { class: 'fb-sw' }, [
          el('h3', { class: 'fb-swh tone-' + tone }, [WB.icon(icon, { size: 13, stroke: 2 }), kind === 'Strength' ? 'Strengths' : 'Weaknesses']),
          rows.length ? el('dl', { class: 'fb-swl' }, rows.flatMap((r) => [el('dt', null, cellNode(sw, r, 'label')), el('dd', null, cellNode(sw, r, 'text'))])) : WB.conditionLine('None recorded.'),
        ]);
      };
      kids.push(el('div', { class: 'fb-2col' }, [col('Strength', 'tick', 'pos'), col('Weakness', 'cross', 'neg')]));
    } else kids.push(WB.conditionLine('No strengths and weaknesses in this run.'));
    return P({ title: 'Credit view, strengths and weaknesses', anchor: 'credit-view', owner: 'CP-2', tables: ['snapshot.credit_view', 'snapshot.strengths_weaknesses'], linkAnchor: 't-snapshot.strengths_weaknesses', body: el('div', { class: 'fb-pbody fb-pad' }, kids) });
  }
  function thesisPanel() {
    const th = T('snapshot.thesis');
    const kids = [];
    if (th && th.rows.length) kids.push(el('p', { class: 'fb-thesis' }, [el('b', null, 'Thesis. '), cellNode(th, 0, 'thesis')]));
    else kids.push(WB.conditionLine('No thesis in this run.'));
    const ca = T('snapshot.catalysts');
    if (ca && ca.rows.length) kids.push(subh('Catalysts'), WB.renderTable(ca, { maxRows: 10 }));
    const ch = T('cp6.challenge');
    if (ch && ch.rows.length) kids.push(subh('Challenge'), cards(ch, { title: 'claim', fields: [['Counter-evidence', 'counter_evidence'], ['Resolution', 'resolution'], ['What would change the view', 'what_would_change_view']] }));
    return P({ title: 'Thesis, catalysts and challenge', anchor: 'thesis', owner: 'CP-6', tables: ['snapshot.thesis', 'snapshot.catalysts', 'cp6.challenge'], linkAnchor: 't-snapshot.thesis', body: el('div', { class: 'fb-pbody fb-pad' }, kids) });
  }
  function limitationsPanel() {
    return P({ title: 'Limitations that bind the decision', anchor: 'binding-limitations', tables: ['cp5.limitations'], body: tableOrCond('cp5.limitations', (t) => WB.renderTable(t, { maxRows: 16 })) });
  }

  function decisionPage(canvas, run) {
    const cfg = WB.callConfig(run);
    const pr = T('cp6.portfolio_recommendation');
    // the instrument in the analyst's shorthand ("Secured 2032s"), as content doc 06 writes the tile's sub-line
    const shortName = (n) =>
      String(n)
        .replace(/^CEI /, '')
        .replace(/^Senior Secured Notes due (\d{4})$/i, 'Secured $1s')
        .replace(/^Senior Notes due (\d{4})(?: \(unsecured\))?$/i, 'Unsecured $1s');
    const finals = [];
    const tiles = [];
    cfg.tiles.forEach((t) => {
      if (t.key === 'final') {
        let tt = t;
        if (t.ref && pr && t.ref.table === pr.id) {
          const r = t.ref.r;
          const v = V(pr, r, 'fit_verdict');
          const cap = String(V(pr, r, 'cap'));
          tt = Object.assign({}, t, { sub: shortName(V(pr, r, 'instrument')) + ', ' + v + (v === 'Fits' ? ', no cap' : ', cap ' + cap) });
        }
        finals.push(tt);
      } else tiles.push(t);
    });
    // per Strategy first, then per portfolio after the Fit cap, each group on its own row
    if (finals.length) tiles.push({ rowBreak: true }, ...finals);
    const items = [];
    const add = (node, label, owners, span) => items.push(item(node, label, owners, span));
    add(portfolioRecPanel(run), 'Portfolio recommendation', ['CP-6']);
    fitPanels(run).forEach((x) => items.push(x));
    if (!(run.fit || []).length) items.push({ node: condPanel('Portfolio Fit', 'FIT', 'Not run: this Pathway attaches no portfolio, so there is no Fit verdict.', 'portfolio-fit'), label: 'Portfolio Fit', na: true });
    add(instrumentPanel(), 'Instrument decision', ['CP-3', 'CP-6']);
    add(capitalPanel(), 'Capital structure', ['MODEL']);
    add(strengthsPanel(), 'Credit view, strengths and weaknesses', ['CP-2']);
    add(thesisPanel(), 'Thesis, catalysts and challenge', ['CP-6']);
    add(limitationsPanel(), 'Limitations that bind the decision', ['CP-5']);
    assemble(canvas, run, { title: 'Portfolio decision', tiles, lines: cfg.lines, items, honest: 'Honest state: the live CAOS run produced no Recommendation', usedBlocks: [] });
  }

  WB.registerFrontPage('covenant_refinancing', covenantPage);
  WB.registerFrontPage('distressed_restructuring', distressPage);
  WB.registerFrontPage('portfolio_decision', decisionPage);
})();
