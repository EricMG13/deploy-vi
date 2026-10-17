/* WB Front Pages A: Credit Snapshot, Earnings Update, Relative Value (bespoke compositions, registered through WB.registerFrontPage).
   Every figure comes from the run (front_page_blocks, handoff tables, charts whose `where` is front_page:<n>); a block that is not shown is a condition line;
   every panel links to its owner module. No chart summary from the fixture is shown: charts get no summary line. */
(function () {
  'use strict';
  const WB = window.WB;
  const el = WB.el;

  /* ---------- small helpers ---------- */
  const QUESTION_TOOLS = (root) => WB.collapseTool(() => root);
  const col = (t, name) => t.columns.indexOf(name);
  const val = (t, r, name) => t.rows[r][col(t, name)];
  const cellRef = (t, r, name) => ({ t: 'cell', table: t.id, r, c: col(t, name) });
  const empty = (v) => WB.isEmpty(v);
  const block = (run, id) => (run.front_page_blocks || []).find((b) => b.id === id) || null;
  /* a cell, rendered by the shared renderer (provenance mark, inspector passport, gap chip, citations) */
  const cell = (t, r, name, label) => (label ? WB.labelCell(WB.renderCell(t, r, col(t, name)).node, label) : WB.renderCell(t, r, col(t, name)).node);
  const planHas = (run, id) => (run.plan || []).includes(id);
  const fmtDate = (iso) => WB.fmtDate(iso);

  /* a chart from the run by id, with no fixture summary; a missing or declared n/a chart is handled by the slot.
     Every chart on these pages sits under a panel title or a sub-heading that names it, so the caption is for assistive technology. */
  function chart(run, id, opts) {
    const c = (run.charts || []).find((x) => x.chart_id === id);
    if (!c) return WB.conditionLine('The chart "' + WB.chartTitle(id) + '" is not in this run.');
    return WB.chartSlot(c, Object.assign({ caption: false }, opts || {}));
  }
  /* a run table as a dense table, or a condition line when the table is absent or has no rows */
  function table(tid, opts) {
    const t = typeof tid === 'string' ? WB.table(tid) : tid;
    if (!t) return WB.conditionLine('Table ' + tid + ' is not in this run.');
    if (!t.rows.length) return WB.conditionLine(opts && opts.none ? opts.none : WB.tableTitle(t.id) + ' has no rows in this run.', { module: WB.citeModule(t.owner) });
    const w = WB.renderTable(t, Object.assign({ anchor: t.id }, opts || {}));
    if (opts && opts.heads) relabel(w, t, opts);
    return w;
  }
  /* replace column heads (period labels from the run) without touching the table's cells */
  function relabel(wrap, t, opts) {
    const kinds = WB.columnKinds(t).filter((k) => k.kind !== 'hidden' && !(opts.hide || []).includes(k.name));
    const ths = WB.qsa('thead th', wrap);
    kinds.forEach((k, i) => {
      if (opts.heads[k.name] && ths[i]) ths[i].textContent = opts.heads[k.name];
    });
  }
  const sub = (text) => el('h3', { class: 'sub-h' }, text);
  const allEmpty = (t) => t.rows.length > 0 && t.rows.every((row) => row.every((v, i) => t.columns[i] === 'cite' || empty(v)));

  /* a table whose rows are all n/a (a blocked module): the reason, with its gap chips, stands in for a row of n/a cells */
  function tableOrReason(tid, reason, opts) {
    const t = WB.table(tid);
    if (t && allEmpty(t)) return WB.conditionLine(reason, { module: WB.citeModule(t.owner), cls: 'fpa-reason' });
    return table(tid, opts);
  }

  /* row of table t whose key column equals key, or -1 */
  const rowOf = (t, keyCol, key) => (t ? t.rows.findIndex((x) => x[col(t, keyCol)] === key) : -1);
  /* append a column to a rendered dense table; fn(r) returns {node, cls} for the row's data-r or null (n/a). Cells come from the real run tables. */
  function addColumn(wrap, head, fn, none) {
    const tbl = wrap.querySelector('table');
    if (!tbl) return wrap;
    const hr = tbl.querySelector('thead tr');
    hr.insertBefore(el('th', { scope: 'col', class: 'h-scale' }, head), hr.querySelector('.h-src'));
    WB.qsa('tbody tr[data-r]', tbl).forEach((tr) => {
      const c = fn(+tr.dataset.r);
      const td = c ? el('td', { class: c.cls }, c.node) : el('td', { class: 'c-gap' }, WB.gapChip([], { label: 'n/a', reason: none || 'No row for this item in the source table.' }));
      tr.insertBefore(td, tr.querySelector('.c-src'));
    });
    WB.initGrid(tbl);
    return wrap;
  }
  function lookup(t, keyCol, key, name, fallback) {
    if (!t) return fallback;
    const r = t.rows.findIndex((x) => x[col(t, keyCol)] === key);
    return r < 0 ? fallback : t.rows[r][col(t, name)];
  }


  /* one-line summaries for collapsed panels, counted from the run's own tables */
  const tally = (t, name) => {
    if (!t || !t.rows.length) return null;
    const m = new Map();
    t.rows.forEach((row) => m.set(row[col(t, name)], (m.get(row[col(t, name)]) || 0) + 1));
    return Array.from(m.entries()).map(([k, n]) => n + ' ' + k).join(', ');
  };
  const plain = (t, name) => (t && t.rows.length ? String(val(t, 0, name)) : '');
  const profileNote = () => {
    const cp = WB.table('snapshot.company_profile');
    if (!cp || !cp.rows.length) return null;
    const bits = ['Ticker ' + plain(cp, 'ticker')];
    ['corp_rating_moodys:Moody\u2019s', 'corp_rating_sp:S&P'].forEach((x) => {
      const [c, l] = x.split(':');
      if (!empty(plain(cp, c))) bits.push(l + ' ' + plain(cp, c));
    });
    return bits.join('; ');
  };

  const levelNote = () => {
    const lv = WB.table('snapshot.instrument_levels');
    if (!lv || !lv.rows.length) return null;
    const n = lv.rows.filter((row) => !empty(row[col(lv, 'mid')])).length;
    return n + ' of ' + lv.rows.length + ' instruments carry a level';
  };

  /* the honest state: tables that carry illustrative verdict words say so while the real-run toggle is on */
  const honestNote = () => (WB.state.honest ? WB.conditionLine('Real-run state: the live CAOS run produced none of the Recommendation, Valuation or preference words in this panel. They are the illustrative design values.', { cls: 'fpa-honest' }) : null);

  /* panel with owner link, tags and the Blocked state taken from the run */
  function P(o) {
    const real = (o.tables || []).map((id) => WB.table(id)).filter(Boolean);
    const owner = o.owner || (real[0] && real[0].owner) || null;
    const ow = owner === 'RUN_BRIEF' ? WB.citeModule('RUN_BRIEF') : owner;
    const tags = o.tags || [];
    if (!o.tags) real.forEach((t) => WB.tableTags(t).forEach((x) => !tags.find((y) => y.kind === x.kind) && tags.push(x)));
    const blocked = ow && WB.stepStatus(ow) === 'blocked';
    const href = ow && WB.ownerHref(ow);
    const link = o.noLink || !href ? null : { href: href + (real[0] && ow === real[0].owner ? '/t-' + WB.cssId(real[0].id) : ''), label: 'Full analysis' };
    return WB.panel({
      title: o.title,
      code: o.code || (owner === 'RUN_BRIEF' ? 'BRIEF' : owner),
      tags,
      state: blocked ? { word: 'Blocked', tone: 'neg', icon: 'status-blocked' } : o.state || null,
      note: o.note || null,
      anchor: o.anchor,
      link,
      body: o.body,
      collapsed: o.collapsed,
      collapsible: o.collapsible,
      className: ['fpa-panel', o.className].filter(Boolean).join(' '),
    });
  }
  const condPanel = (title, anchor, text, code) => WB.panel({ title, code: code || null, anchor, collapsible: false, className: 'panel-cond', note: text, body: null });

  /* the page: verdict bar, then a 12-column grid of items {id, label, node, span, na, owner} */
  function assemble(canvas, run, barFrag, items) {
    const root = el('div', { class: 'view view-front fpa' });
    canvas.appendChild(root);
    root.appendChild(barFrag(root));
    // the page added or removed call lines after the bar was built: cap them again in the content doc's order
    WB.capCallLines(root.querySelector('.verdict-lines'));
    const grid = el('div', { class: 'fp-grid' });
    items.forEach((it) => {
      it.node.style.gridColumn = 'span ' + (it.span || 12);
      grid.appendChild(it.node);
    });
    root.appendChild(grid);
    WB.setOutline(items.map((it) => ({ id: it.id, label: it.label, na: !!it.na })));
    const mods = new Set();
    items.forEach((it) => (it.owners || []).forEach((o) => o && o !== 'RUN_BRIEF' && mods.add(WB.citeModule(o))));
    WB.page.gapModules = Array.from(mods);
  }
  const item = (node, label, anchor, span, owners, na) => ({ node, label, id: 'p-' + WB.cssId(anchor), span, owners, na });

  /* a not-shown block: one condition line with the run's own reason */
  function notShown(run, blockId, title, anchor, code) {
    const b = block(run, blockId);
    const why = b && b.reason ? 'Not shown: ' + b.reason + '.' : 'Not shown.';
    return item(condPanel(title, anchor, why, code), title, anchor, 12, [], true);
  }

  /* ---------- the verdict bar with page-specific call lines ---------- */
  function callLine(label, tone, children) {
    return el('p', { class: 'v-line' }, [el('span', { class: 'v-ll tone-' + tone }, label), ' ', children]);
  }
  function callBar(run, extra, notices) {
    const frag = WB.callBar(run, extra, notices);
    const lines = frag.querySelector('.verdict-lines');
    const find = (label) => (lines ? WB.qsa('.v-line', lines).find((p) => p.querySelector('.v-ll') && p.querySelector('.v-ll').textContent === label) : null);
    return { frag, lines, find };
  }
  const ref = (desc, text, cls) => el('button', { type: 'button', class: 'fpa-ref ' + (cls || ''), 'data-ref': WB.ref(desc) }, text);

  /* ---------- shared panels ---------- */
  const SLOT = { fy_2: 'FY-2', fy_1: 'FY-1', fy: 'FY', pytd: 'PYTD', ytd: 'YTD', ltm: 'LTM' };
  function periodHeads() {
    const fc = WB.table('snapshot.financial_columns');
    const out = {};
    if (!fc) return out;
    Object.keys(SLOT).forEach((name) => {
      const r = fc.rows.findIndex((x) => x[col(fc, 'slot')] === SLOT[name]);
      if (r >= 0) out[name] = fc.rows[r][col(fc, 'label')];
    });
    return out;
  }

  /* tabs: a tablist with roving tabindex; panels hidden except the selected one */
  function tabs(prefix, items, startKey) {
    let cur = startKey || items[0].key;
    const bar = el('div', { class: 'fpa-tabs', role: 'tablist', 'aria-label': 'Views of this panel' });
    const panes = el('div', { class: 'fpa-panes' });
    const btns = {};
    const nodes = {};
    const set = (key, focus) => {
      cur = key;
      items.forEach((it) => {
        const on = it.key === key;
        btns[it.key].setAttribute('aria-selected', on ? 'true' : 'false');
        btns[it.key].setAttribute('tabindex', on ? '0' : '-1');
        btns[it.key].classList.toggle('on', on);
        nodes[it.key].hidden = !on;
      });
      if (focus) btns[key].focus();
    };
    items.forEach((it) => {
      const id = prefix + '-' + it.key;
      const b = el('button', { type: 'button', role: 'tab', id: 'tab-' + id, class: 'fpa-tab', 'aria-controls': 'tp-' + id }, it.label);
      b.addEventListener('click', () => set(it.key));
      b.addEventListener('keydown', (e) => {
        if (!['ArrowLeft', 'ArrowRight', 'Home', 'End'].includes(e.key)) return;
        e.preventDefault();
        const i = items.findIndex((x) => x.key === cur);
        const n = e.key === 'Home' ? 0 : e.key === 'End' ? items.length - 1 : (i + (e.key === 'ArrowRight' ? 1 : -1) + items.length) % items.length;
        set(items[n].key, true);
      });
      btns[it.key] = b;
      bar.appendChild(b);
      const pane = el('div', { class: 'fpa-pane', role: 'tabpanel', id: 'tp-' + id, 'aria-labelledby': 'tab-' + id }, it.node);
      nodes[it.key] = pane;
      panes.appendChild(pane);
    });
    set(cur);
    return { bar, panes, set };
  }

  /* the Recommendation cell (real instrument_recommendation row) for the facility of row r of table base */
  function recCell(rec, base, r) {
    const ri = rowOf(rec, 'facility_id', base.rows[r][col(base, 'facility_id')]);
    return ri < 0 ? null : WB.renderCell(rec, ri, col(rec, 'recommendation'));
  }

  /* capital structure: facilities with the Recommendation joined by facility, totals, and the debt stack */
  function capStructure(run, withMaturity) {
    const cs = WB.table('snapshot.capital_structure');
    if (!cs) return [WB.conditionLine('Capital structure is not in this run.')];
    if (!cs.rows.length) return [WB.conditionLine('Capital structure has no rows in this run.', { module: WB.citeModule(cs.owner) })];
    const rec = WB.table('snapshot.instrument_recommendation');
    const facTable = table(cs, { maxRows: cs.rows.length, hide: ['facility_id', 'bloomberg_id', 'facility_ratings', 'spread_or_coupon', 'currency', 'unit', 'rank', 'secured', 'structuring_multiple_x', 'column_basis'] });
    if (rec && rec.rows.length) addColumn(facTable, 'Recommendation', (r) => recCell(rec, cs, r), 'The Recommendation table has no row for this facility.');
    const tot = WB.table('snapshot.capital_structure_totals');
    return [
      honestNote(),
      facTable,
      tot ? sub('Totals, enterprise value and multiples') : null,
      tot ? table(tot, { hide: ['structuring_multiple_x', 'basis'] }) : null,
      sub('Debt stack by rank, cumulative multiple'),
      el('div', { class: 'fpa-pad' }, chart(run, 'chart.capital_structure')),
      withMaturity ? sub('Maturity wall') : null,
      withMaturity ? el('div', { class: 'fpa-pad' }, chart(run, 'chart.maturity_wall')) : null,
    ];
  }

  function companyKV(run, full) {
    const cp = WB.table('snapshot.company_profile');
    if (!cp || !cp.rows.length) return WB.conditionLine('No company profile in this run.');
    // a rating and its outlook that are both n/a for the same gaps show one chip, not the same ids twice
    const pair = (a, b, label) => {
      const ga = WB.cellOrigin(cp, 0, col(cp, a)).kind === 'gap' ? WB.cellGap(cp, 0, col(cp, a)) : null;
      const gb = WB.cellOrigin(cp, 0, col(cp, b)).kind === 'gap' ? WB.cellGap(cp, 0, col(cp, b)) : null;
      const same = ga && gb && ga.item && gb.item && ga.item === gb.item;
      return el('span', { class: 'fpa-pair' }, same ? [cell(cp, 0, a, label)] : [cell(cp, 0, a, label), ' ', cell(cp, 0, b, label + ' outlook')]);
    };
    // every cell keeps the label this table shows it under, so its passport is titled as the page reads
    const rows = [
      ['Sector', cell(cp, 0, 'sector', 'Sector')],
      ['Country', cell(cp, 0, 'country', 'Country')],
      ['Ticker', cell(cp, 0, 'ticker', 'Ticker')],
      ['Sponsor Quality', cell(cp, 0, 'sponsor_quality', 'Sponsor Quality')],
      ["Moody's", pair('corp_rating_moodys', 'outlook_moodys', "Moody's")],
      ['S&P', pair('corp_rating_sp', 'outlook_sp', 'S&P')],
      ['Fitch', pair('corp_rating_fitch', 'outlook_fitch', 'Fitch')],
    ];
    if (full) {
      rows.push(['Management', cell(cp, 0, 'management', 'Management')], ['Shareholders', cell(cp, 0, 'shareholders', 'Shareholders')], ['Morningstar issuer ID', cell(cp, 0, 'morningstar_issuer_id', 'Morningstar issuer ID')], ['Listed', cell(cp, 0, 'listed', 'Listed')]);
    }
    const tb = el('tbody');
    rows.forEach(([k, node]) => tb.appendChild(el('tr', null, [el('th', { scope: 'row', class: 'kv-k' }, k), el('td', { class: 'kv-v' }, node)])));
    const tbl = el('table', { class: 'dt kv', 'data-table': cp.id, 'data-grid': '1' }, [el('caption', { class: 'sr-only' }, 'Company profile'), tb]);
    WB.initGrid(tbl);
    return el('div', { class: 'tw' }, tbl);
  }

  /* ---------- Credit Snapshot ---------- */
  function creditSnapshot(canvas, run) {
    const items = [];
    const quick = run.depth === 'quick';
    const cv = WB.table('snapshot.credit_view');
    const barFrag = (root) => {
      // a Quick run's Screening basis is a tag in the byline row (word, icon, module code); its sentence is the tag's passport
      const notices = [];
      if (quick) {
        const basis = cv && cv.rows.length ? val(cv, 0, 'basis') : null;
        const conf = cv && cv.rows.length ? val(cv, 0, 'confidence') : null;
        const fields = [['Basis', basis || 'Screening', false]];
        if (conf) fields.push(['Confidence', conf, false]);
        fields.push(['Reading', 'This run is at ' + (basis || 'Screening') + ' basis (Quick depth): the Recommendations, Credit Score and Direction rest on a screen, not the full assessment.', false]);
        const code = cv ? WB.citeModule(cv.owner) : 'CP-2';
        notices.push({ word: 'Screening basis', tone: 'cau', icon: 'info', code, desc: { t: 'note', kind: 'none', code, title: 'Screening basis (Quick depth)', sub: WB.moduleName(code) + ' (' + code + ')', fields, note: 'A Quick run screens the issuer; it does not carry the full assessment.' } });
      }
      return callBar(run, QUESTION_TOOLS(root), notices).frag;
    };

    // key findings (CP-2 credit view, CP-1 performance, CP-6 catalysts) beside company and operating model (CP-1A)
    const hp = WB.table('snapshot.historical_performance');
    const cat = WB.table('snapshot.catalysts');
    const kf = [];
    if (cv && cv.rows.length) {
      kf.push(['Support', cell(cv, 0, 'primary_support'), 'pos']);
      kf.push(['Main risk', cell(cv, 0, 'primary_downside'), 'neg']);
    }
    if (hp && hp.rows.length) kf.push(['The period', cell(hp, 0, 'text'), 'neu']);
    if (cat && cat.rows.length) {
      const nr = cat.rows.findIndex((x) => !/passed/i.test(x[col(cat, 'date_or_window')]));
      if (nr >= 0) kf.push(['Next', el('span', null, [el('span', { class: 'num fpa-date' }, val(cat, nr, 'date_or_window')), ' ', cell(cat, nr, 'event'), ' ', el('span', { class: 'muted' }, 'Watch: '), cell(cat, nr, 'watch_trigger')]), 'neu']);
    }
    const kfBody = kf.length
      ? el('ol', { class: 'fpa-kf' }, kf.map(([k, node, tone]) => el('li', null, [el('span', { class: 'fpa-kf-k tone-' + tone }, k), el('div', { class: 'fpa-kf-v' }, node)])))
      : WB.conditionLine('No credit view or performance text in this run.');
    items.push(item(P({ title: 'Key findings', tables: ['snapshot.credit_view'], anchor: 'fp-key-findings', body: kfBody, tags: cv ? WB.tableTags(cv) : [] }), 'Key findings', 'fp-key-findings', 6, ['CP-2']));

    const bd = WB.table('snapshot.business_description');
    const companyBody = [bd && bd.rows.length ? el('div', { class: 'fpa-desc' }, cell(bd, 0, 'description')) : WB.conditionLine('No business description in this run.'), companyKV(run, false)];
    items.push(item(P({ title: 'Company and operating model', tables: ['snapshot.business_description', 'snapshot.company_profile'], anchor: 'fp-company', body: companyBody }), 'Company and operating model', 'fp-company', 6, ['CP-1A']));

    // the strip: net leverage, interest cover and liquidity side by side (the maturity wall sits with the debt stack below)
    const stripBody = el('div', { class: 'fpa-strip' }, chart(run, 'chart.model_strip', { compact: true }));
    items.push(item(P({ title: 'Model chart strip', owner: 'MODEL', anchor: 'fp-strip', body: stripBody, tags: [] }), 'Model chart strip', 'fp-strip', 12, ['MODEL']));

    // capital structure with tabs
    const heads = periodHeads();
    const ebitda = el('div', null, [table('snapshot.ebitda_adjustments', { hide: ['basis'] }), sub('EBITDA bridge'), el('div', { class: 'fpa-pad' }, chart(run, 'chart.ebitda_bridge'))]);
    const fin = el('div', null, [table('snapshot.financials', { maxRows: 40, hide: ['line_id', 'section'], heads })]);
    const metrics = el('div', null, [table('model.metrics', { maxRows: 40, hide: ['metric_id'], heads })]);
    const tb = tabs('cs', [
      { key: 'cs', label: 'Capital structure', node: el('div', null, capStructure(run, true)) },
      { key: 'ebitda', label: 'EBITDA adjustments', node: ebitda },
      { key: 'fin', label: 'Financials', node: fin },
      { key: 'metrics', label: 'Credit metrics', node: metrics },
    ]);
    items.push(item(P({ title: 'Capital structure and financials', tables: ['snapshot.capital_structure'], owner: 'MODEL', anchor: 'fp-capital', body: [tb.bar, tb.panes], tags: [] }), 'Capital structure and financials', 'fp-capital', 12, ['MODEL']));

    // strengths and weaknesses with the thesis
    const sw = WB.table('snapshot.strengths_weaknesses');
    const th = WB.table('snapshot.thesis');
    const list = (kind, icon, tone) => {
      const rows = sw ? sw.rows.map((r, i) => i).filter((i) => sw.rows[i][col(sw, 'kind')] === kind) : [];
      return el('div', { class: 'fpa-sw-col' }, [
        el('h3', { class: 'fpa-sw-h tone-' + tone }, [WB.icon(icon, { size: 13, stroke: 2 }), kind === 'Strength' ? 'Strengths' : 'Weaknesses']),
        rows.length
          ? el('dl', { class: 'fpa-sw' }, rows.map((i) => [el('dt', null, cell(sw, i, 'label')), el('dd', null, cell(sw, i, 'text'))]))
          : WB.conditionLine('No ' + kind.toLowerCase() + 's in this run.'),
      ]);
    };
    const swBody = [
      th && th.rows.length ? el('p', { class: 'fpa-thesis' }, [el('strong', null, 'Thesis. '), cell(th, 0, 'thesis')]) : WB.conditionLine('No thesis in this run.'),
      sw ? el('div', { class: 'fpa-cols fpa-pad' }, [list('Strength', 'tick', 'pos'), list('Weakness', 'cross', 'neg')]) : WB.conditionLine('Strengths and weaknesses are not in this run.'),
      cat && cat.rows.length ? sub('Catalysts and near-term events') : null,
      cat && cat.rows.length ? table(cat, { hide: [] }) : null,
    ];
    items.push(item(P({ title: 'Strengths and weaknesses', tables: ['snapshot.strengths_weaknesses', 'snapshot.thesis'], owner: 'CP-2', anchor: 'fp-sw', body: swBody }), 'Strengths and weaknesses', 'fp-sw', 12, ['CP-2', 'CP-6']));

    // collapsed panels: relative value, company profile, transaction summary, valuation per instrument, Portfolio Fit, committee challenge
    const rvBody = [table('snapshot.relative_value', { maxRows: 16, hide: ['bloomberg_id'] }), el('div', { class: 'fpa-cols fpa-pad' }, [chart(run, 'chart.rv_loan'), chart(run, 'chart.rv_hy')])];
    items.push(item(P({ title: 'Relative value', tables: ['snapshot.relative_value'], owner: 'CP-3', anchor: 'fp-rv', body: rvBody, collapsed: true, note: tally(WB.table('snapshot.relative_value'), 'block') }), 'Relative value', 'fp-rv', 12, ['CP-3']));

    items.push(item(P({ title: 'Company profile', tables: ['snapshot.company_profile'], owner: 'CP-1A', anchor: 'fp-profile', body: companyKV(run, true), collapsed: true, note: profileNote() }), 'Company profile', 'fp-profile', 12, ['CP-1A']));

    if (run.primary) {
      const ts = WB.table('snapshot.transaction_summary');
      items.push(item(P({ title: 'Transaction summary and new debt issues', tables: [], owner: 'CP-1A', code: 'Primary', anchor: 'fp-transaction', body: ts ? table(ts, { hide: ['bloomberg_id', 'borrower', 'currency', 'unit', 'use_of_proceeds', 'commitment_date', 'analyst_value'] }) : WB.conditionLine('The transaction summary is not in this run.'), collapsed: true, note: ts ? ts.rows.length + ' tranche' + (ts.rows.length === 1 ? '' : 's') + ' in the new-debt table' : null, tags: ts ? WB.tableTags(ts) : [] }), 'Transaction summary', 'fp-transaction', 12, ['CP-1A']));
    } else {
      items.push(item(condPanel('Transaction summary and new debt issues', 'fp-transaction', 'Transaction summary: not a Primary run.', 'CP-1A'), 'Transaction summary', 'fp-transaction', 12, [], true));
    }

    const valBody = [honestNote(), table('snapshot.instrument_levels', { maxRows: 16, hide: ['facility_id', 'rationale', 'bid', 'ask', 'oid'] }), WB.table('cp3.talk_valuation') && WB.table('cp3.talk_valuation').rows.length ? sub('Talk against comparables') : null, WB.table('cp3.talk_valuation') && WB.table('cp3.talk_valuation').rows.length ? table('cp3.talk_valuation', { hide: ['facility_id', 'comparable_basis', 'metric_basis', 'implied_low', 'implied_high'] }) : null, el('div', { class: 'fpa-pad' }, run.charts.some((c) => c.chart_id === 'chart.talk_range') ? chart(run, 'chart.talk_range') : null)];
    items.push(item(P({ title: 'Valuation per instrument', tables: ['snapshot.instrument_levels'], owner: 'CP-3', anchor: 'fp-valuation', body: valBody, collapsed: true, note: levelNote() }), 'Valuation per instrument', 'fp-valuation', 12, ['CP-3']));

    items.push(item(portfolioFitPanel(run, true), 'Portfolio Fit', 'fp-fit', 12, ['FIT', 'CP-6']));

    const ch = WB.table('cp6.challenge');
    items.push(item(P({ title: 'Committee challenge', tables: ['cp6.challenge'], owner: 'CP-6', anchor: 'fp-challenge', body: ch ? table(ch, { hide: [] }) : WB.conditionLine('The committee challenge did not run in this Pathway.'), collapsed: true, note: ch && ch.rows.length ? ch.rows.length + ' claims challenged' : null }), 'Committee challenge', 'fp-challenge', 12, ['CP-6']));

    const wc = block(run, 'credit_snapshot.19');
    items.push(notShown(run, wc ? wc.id : 'credit_snapshot.19', 'What changed since the last Report', 'fp-changed', 'CP-8'));
    assemble(canvas, run, barFrag, items);
  }

  function portfolioFitPanel(run, collapsed) {
    const pf = WB.table('snapshot.portfolio_fit');
    const pr = WB.table('cp6.portfolio_recommendation');
    if (!pf || !pf.rows.length) return condPanel('Portfolio Fit', 'fp-fit', 'Not run in this Pathway: no portfolio is attached, so there is no Fit verdict.', 'FIT');
    const body = [table(pf, { maxRows: 16, hide: ['portfolio_id', 'facility_id', 'current_exposure', 'reason'] }), el('div', { class: 'fpa-pad' }, run.charts.some((c) => c.chart_id === 'chart.fit_bullets') ? chart(run, 'chart.fit_bullets') : null)];
    if (pr && pr.rows.length) body.splice(1, 0, sub('Recommendation per portfolio'), table(pr, { maxRows: 12, hide: ['portfolio_id', 'reason'] }));
    return P({ title: 'Portfolio Fit', tables: ['snapshot.portfolio_fit'], owner: 'FIT', anchor: 'fp-fit', body, collapsed, note: collapsed ? tally(pf, 'verdict') : null });
  }

  /* ---------- Earnings Update ---------- */
  const CHANGE_ICON = { improved: 'arrow-up', deteriorated: 'arrow-down', unchanged: 'arrow-flat', new: 'plus', removed: 'minus' };
  /* a value column that mixes numbers and words: numbers become figures with a passport, words stay text */
  function valueFig(t, r, name) {
    const c = col(t, name);
    const v = t.rows[r][c];
    if (empty(v) || !WB.isNumeric(String(v))) return { node: WB.renderCell(t, r, c).node, cls: 'c-text' };
    const o = WB.cellOrigin(t, r, c);
    const shown = WB.fmtByUnit(t, r, c) || WB.fmtNum(v);
    return { node: WB.fig({ t: 'cell', table: t.id, r, c }, shown, { kind: o.kind, label: WB.figLabel(shown, o.kind) }), cls: 'c-num' };
  }
  const proseCell = (t, r, name) => ({ node: WB.renderCell(t, r, col(t, name)).node, cls: 'c-prose' });
  function changeChip(t, r, name) {
    const word = String(val(t, r, name));
    const sg = WB.signal(word);
    const icon = CHANGE_ICON[word.toLowerCase()] || sg.icon;
    const tone = ['improved', 'deteriorated'].includes(word.toLowerCase()) ? sg.tone : 'neu';
    const content = el('span', { class: 'chip tone-' + tone }, [icon ? WB.icon(icon, { size: 12, stroke: 2 }) : null, word]);
    return WB.fig({ t: 'cell', table: t.id, r, c: col(t, name) }, content, { kind: 'none', noMark: true, label: name + ': ' + word, cls: 'fpa-chg' });
  }
  /* a table of chosen columns where named columns are drawn by the page */
  function custom(t, names, draw, opts) {
    const o = opts || {};
    const kinds = WB.columnKinds(t);
    const kindOf = (n) => (col(t, n) >= 0 ? kinds[col(t, n)] : { kind: 'text', label: WB.colLabel(n) });
    const ths = names.map((n) => el('th', { scope: 'col', class: 'h-' + kindOf(n).kind }, (o.heads && o.heads[n]) || kindOf(n).label));
    const tbody = el('tbody');
    t.rows.forEach((row, r) => {
      const tr = el('tr', { 'data-r': r });
      names.forEach((n, i) => {
        const d = draw && draw[n] ? draw[n](t, r, n) : null;
        const c = d ? (d.node ? d : { node: d, cls: 'c-text' }) : WB.renderCell(t, r, col(t, n));
        tr.appendChild(el(i === 0 && o.rowHead ? 'th' : 'td', { class: c.cls + (i === 0 && o.rowHead ? ' c-rowh' : ''), scope: i === 0 && o.rowHead ? 'row' : false }, c.node));
      });
      tbody.appendChild(tr);
    });
    const tbl = el('table', { class: 'dt', 'data-table': t.id, 'data-grid': '1' }, [el('caption', { class: 'sr-only' }, o.caption || WB.tableTitle(t.id)), el('thead', null, el('tr', null, ths)), tbody]);
    WB.initGrid(tbl);
    return el('div', { class: 'tw' }, tbl);
  }

  function whatChanged(run, b) {
    const wc = WB.table('cp8.what_changed');
    const rc = WB.table('cp8.recommendation_change');
    if (!wc || !wc.rows.length) return item(condPanel('What changed since the last Report', 'fp-changed', 'The run has no what-changed rows.', 'CP-8'), 'What changed', 'fp-changed', 12, [], true);
    const ci = col(wc, 'change');
    const counts = new Map();
    wc.rows.forEach((row) => counts.set(row[ci], (counts.get(row[ci]) || 0) + 1));
    const order = ['Deteriorated', 'Improved', 'Unchanged', 'New', 'Removed'];
    const summary = el('div', { class: 'fpa-chg-sum', role: 'list', 'aria-label': 'Change kinds' }, Array.from(counts.keys()).sort((a, b2) => order.indexOf(a) - order.indexOf(b2)).map((k) => {
      const sg = WB.signal(k);
      const tone = ['Improved', 'Deteriorated'].includes(k) ? sg.tone : 'neu';
      return el('span', { role: 'listitem', class: 'chip tone-' + tone }, [WB.icon(CHANGE_ICON[k.toLowerCase()] || 'arrow-flat', { size: 12, stroke: 2 }), counts.get(k) + ' ' + k.toLowerCase()]);
    }));
    const pc = run.prior_case || {};
    const note = pc.report_date ? 'Compared with the Report of ' + fmtDate(pc.report_date) : null;
    const body = [
      el('div', { class: 'fpa-pad fpa-chg-head' }, [summary, note ? el('span', { class: 'muted' }, note) : null]),
      custom(wc, ['field', 'prior_value', 'current_value', 'change', 'why'], { field: (t, r) => ({ node: el('div', null, [WB.renderCell(t, r, col(t, 'field')).node, el('div', { class: 'fpa-sub' }, WB.renderCell(t, r, col(t, 'block')).node)]), cls: 'c-text' }), change: (t, r, n) => changeChip(t, r, n), prior_value: valueFig, current_value: valueFig, why: proseCell }, { rowHead: false, heads: { field: 'Item and block', prior_value: 'Prior', current_value: 'Current', change: 'Change', why: 'Why' } }),
      rc && rc.rows.length ? sub('Recommendation change') : null,
      rc && rc.rows.length ? table(rc, {}) : null,
      sub('Prior and current values'),
      el('div', { class: 'fpa-pad' }, chart(run, 'chart.what_changed')),
    ];
    return item(P({ title: 'What changed since the last Report', tables: ['cp8.what_changed'], owner: 'CP-8', anchor: 'fp-changed', body, tags: WB.tableTags(wc) }), 'What changed', 'fp-changed', 12, ['CP-8']);
  }

  function earningsUpdate(canvas, run) {
    const items = [];
    const barFrag = (root) => {
      const b = callBar(run, QUESTION_TOOLS(root));
      if (b.lines) {
        const wi = WB.table('cp2.watch_items');
        if (wi && wi.rows.length) {
          const kids = [];
          wi.rows.slice(0, 2).forEach((_, i) => {
            if (i) kids.push('; ');
            kids.push(el('b', null, val(wi, i, 'trigger')), ': ', WB.inline(String(val(wi, i, 'threshold_or_signal')).replace(/\.\s*$/, ''), 'CP-2'));
          });
          b.lines.appendChild(callLine('WATCH', 'cau', kids));
        }
        const absent = ['CP-3', 'CP-6', 'FIT'].filter((id) => !planHas(run, id));
        if (absent.length) {
          const names = absent.map((id) => (id === 'FIT' ? 'Portfolio Fit' : id));
          // fixed copy: its lead is written here, since the sentence has commas of its own
          b.lines.appendChild(callLine('NO RECOMMENDATION', 'neu', [el('strong', { class: 'v-lead' }, 'No Recommendation, Valuation or Fit'), ': this Pathway runs no ' + names.slice(0, -1).join(', ') + (names.length > 1 ? ' or ' : '') + names[names.length - 1] + '. The page answers whether the credit view moves, not whether to own the issuer.']));
        }
      }
      return b.frag;
    };
    const headline = [
      table('cp1b.period_comparison', { hide: ['comparison_basis', 'restatement', 'reference_period_id', 'current_period_id'], maxRows: 14, heads: { metric_id: 'Metric', current_value: 'Current', reference_value: 'Reference', abs_change: 'Change', pct_change_pct: 'Change %', perimeter_change: 'Perimeter change' } }),
      el('div', { class: 'fpa-pad' }, chart(run, 'chart.headline_results')),
    ];
    items.push(item(P({ title: 'Headline results', tables: ['cp1b.period_comparison'], anchor: 'fp-headline', body: headline }), 'Headline results', 'fp-headline', 12, ['CP-1B']));
    items.push(item(P({ title: 'Variance drivers', tables: ['cp1b.variance_drivers'], anchor: 'fp-variance', body: table('cp1b.variance_drivers', {}) }), 'Variance drivers', 'fp-variance', 12, ['CP-1B']));

    const wcb = block(run, 'earnings_update.13');
    if (wcb && wcb.shown) items.push(whatChanged(run, wcb));
    else items.push(notShown(run, 'earnings_update.13', 'What changed since the last Report', 'fp-changed', 'CP-8'));

    const kb = block(run, 'earnings_update.6');
    const kpi = WB.table('cp1b.kpi_changes');
    if (kb && kb.shown && kpi && kpi.rows.length) {
      items.push(item(P({ title: 'KPI changes', tables: ['cp1b.kpi_changes'], anchor: 'fp-kpi', body: el('div', { class: 'fpa-split' }, [table(kpi, {}), el('div', { class: 'fpa-pad' }, chart(run, 'chart.kpi_changes'))]) }), 'KPI changes', 'fp-kpi', 12, ['CP-1B']));
    } else items.push(item(condPanel('KPI changes', 'fp-kpi', 'Not shown: no KPI rows in this run.', 'CP-1B'), 'KPI changes', 'fp-kpi', 12, [], true));

    const gd = WB.table('cp1b.guidance_vs_delivery');
    let guidance;
    if (!gd || !gd.rows.length || allEmpty(gd)) {
      const gi = WB.gapItems('CP-1B').find((g) => /guidance/i.test(g.text));
      guidance = WB.conditionLine(gi ? 'Guidance against delivery: n/a. ' + gi.text : 'Guidance against delivery: not provided in this run.', { module: 'CP-1B' });
    } else guidance = table(gd, {});
    items.push(item(P({ title: 'Guidance and early signals', tables: ['cp1b.signals'], anchor: 'fp-signals', body: [sub('Guidance against delivery'), el('div', { class: 'fpa-pad' }, guidance), sub('Early signals'), table('cp1b.signals', {})] }), 'Guidance and early signals', 'fp-signals', 12, ['CP-1B']));

    const bridge = [table('snapshot.ebitda_adjustments', { hide: ['basis'] }), el('div', { class: 'fpa-pad' }, chart(run, 'chart.ebitda_bridge'))];
    items.push(item(P({ title: 'EBITDA bridge', tables: ['snapshot.ebitda_adjustments'], owner: 'MODEL', anchor: 'fp-bridge', body: bridge }), 'EBITDA bridge', 'fp-bridge', 12, ['MODEL']));

    const hp = WB.table('snapshot.historical_performance');
    const histBody = [hp && hp.rows.length ? el('p', { class: 'fpa-thesis' }, cell(hp, 0, 'text')) : WB.conditionLine('No historical performance text in this run.'), el('div', { class: 'fpa-pad' }, chart(run, 'chart.model_strip', { compact: true }))];
    items.push(item(P({ title: 'Historical performance and leverage strip', tables: ['snapshot.historical_performance'], anchor: 'fp-history', body: histBody }), 'Historical performance', 'fp-history', 12, ['CP-1B', 'MODEL']));

    const heads = periodHeads();
    items.push(item(P({ title: 'Financials', tables: ['snapshot.financials'], owner: 'MODEL', anchor: 'fp-financials', body: table('snapshot.financials', { maxRows: 40, hide: ['line_id', 'section'], heads }), collapsed: true, note: heads.fy_2 && heads.ltm ? heads.fy_2 + ' to ' + heads.ltm : null }), 'Financials', 'fp-financials', 12, ['MODEL']));

    const trig = WB.table('cpl10.upgrade_triggers');
    items.push(item(P({ title: 'Watch items', tables: ['cp2.watch_items'], anchor: 'fp-watch', body: [table('cp2.watch_items', {}), trig && trig.rows.length ? sub('Upgrade triggers') : null, trig && trig.rows.length ? table(trig, {}) : null] }), 'Watch items', 'fp-watch', 12, ['CP-2']));

    items.push(item(P({ title: 'Company profile', tables: ['snapshot.company_profile'], owner: 'CP-1A', anchor: 'fp-profile', body: companyKV(run, true), collapsed: true }), 'Company profile', 'fp-profile', 12, ['CP-1A']));
    assemble(canvas, run, barFrag, items);
  }

  /* ---------- Relative Value ---------- */
  function preferredLine(run) {
    const sp = WB.table('cp3.security_preference');
    const lv = WB.table('snapshot.instrument_levels');
    if (!sp || !sp.rows.length || WB.state.honest) return null;
    const nameOf = (fid) => lookup(lv, 'facility_id', fid, 'instrument', fid);
    const levelRef = (fid, name) => {
      const r = lv ? lv.rows.findIndex((x) => x[col(lv, 'facility_id')] === fid) : -1;
      if (r < 0 || empty(lv.rows[r][col(lv, name)])) return null;
      // the call line prints a yield and a price by unit (8.06%, 93.28); the passport keeps the served value
      const shown = WB.fmtByUnit(lv, r, col(lv, name)) || val(lv, r, name);
      return ref({ t: 'cell', table: lv.id, r, c: col(lv, name) }, name === 'yield_or_dm' ? shown + '%' : shown, 'strong');
    };
    const sentence = (row, word) => {
      const fid = row[col(sp, 'facility_id')];
      const px = levelRef(fid, 'mid');
      const yl = levelRef(fid, 'yield_or_dm');
      const kids = [el('b', null, nameOf(fid))];
      if (px) kids.push(' at ', px);
      if (yl) kids.push(', yield ', yl);
      kids.push(': ', word, '. ');
      kids.push(WB.inline(row[col(sp, 'key_reason')], WB.citeModule(sp.owner)));
      return kids;
    };
    const pref = sp.rows.find((x) => x[col(sp, 'preference')] === 'Preferred');
    const avoid = sp.rows.find((x) => x[col(sp, 'preference')] === 'Avoid');
    const kids = [];
    if (pref) kids.push(...sentence(pref, 'Preferred'));
    if (avoid) kids.push(' ', ...sentence(avoid, 'Avoid'));
    return kids.length ? callLine('PREFERRED', 'pos', kids) : null;
  }

  /* market against fundamentals: implication with its basis beneath; blocked or blank tables give the reason instead */
  function marketTable(reason) {
    const t = WB.table('cp3d.market_vs_fundamental');
    if (!t || !t.rows.length || allEmpty(t)) return tableOrReason('cp3d.market_vs_fundamental', reason, {});
    const withBasis = (t2, r) => ({ node: el('div', null, [WB.renderCell(t2, r, col(t2, 'implication')).node, el('div', { class: 'fpa-sub' }, [el('span', { class: 'fpa-sub-k' }, 'Basis: '), WB.renderCell(t2, r, col(t2, 'basis')).node])]), cls: 'c-prose' });
    return custom(t, ['implication', 'alignment', 'fundamental_evidence', 'open_question'], { implication: withBasis }, { heads: { implication: 'Market implication and basis' } });
  }

  /* implied risk: the security with its model and limitation beneath, then the numbers */
  function impliedTable(reason) {
    const t = WB.table('cp3d.implied_risk');
    if (!t.rows.length || allEmpty(t)) return tableOrReason('cp3d.implied_risk', reason, {});
    // a model and limitation shared by every row are said once, under the table, not repeated on each security
    const same = (n) => t.rows.every((row) => row[col(t, n)] === t.rows[0][col(t, n)]);
    const shared = same('model') && same('limitation') && t.rows.length > 1;
    const withModel = (t2, r) => ({ node: el('div', null, [WB.renderCell(t2, r, col(t2, 'security_id')).node, shared ? null : el('div', { class: 'fpa-sub' }, [WB.renderCell(t2, r, col(t2, 'model')).node]), shared ? null : el('div', { class: 'fpa-sub' }, [el('span', { class: 'fpa-sub-k' }, 'Limit: '), WB.renderCell(t2, r, col(t2, 'limitation')).node])]), cls: 'c-prose' });
    const tbl = custom(t, ['security_id', 'horizon_years', 'recovery_assumption_pct', 'implied_pd_pct', 'implied_loss_pct', 'break_even_spread_bps'], { security_id: withModel }, { heads: { security_id: shared ? 'Security' : 'Security, model and limitation' } });
    if (!shared) return tbl;
    return el('div', null, [tbl, el('p', { class: 'fpa-note' }, [el('span', { class: 'fpa-sub-k' }, 'Model: '), WB.renderCell(t, 0, col(t, 'model')).node, ' ', el('span', { class: 'fpa-sub-k' }, 'Limit: '), WB.renderCell(t, 0, col(t, 'limitation')).node])]);
  }

  function relativeValue(canvas, run) {
    const items = [];
    const blocked = WB.stepStatus('CP-3D') === 'blocked';
    const reason = blocked ? WB.stepReason('CP-3D') || 'CP-3D is blocked in this run.' : '';
    const barFrag = (root) => {
      // a Blocked CP-3D is a tag in the byline row (word, icon, module code); the full sentence lives in the tag's passport and in the module's panels
      const notices = [];
      if (blocked) {
        const why = String(reason).replace(/^Blocked:?\s*/i, '').replace(/\s*$/, '').replace(/([^.!?])$/, '$1.');
        const sentence = 'CP-3D ' + WB.moduleName('CP-3D') + ' is Blocked: ' + why.charAt(0).toLowerCase() + why.slice(1);
        notices.push({ word: 'Blocked', tone: 'neg', icon: 'status-blocked', code: 'CP-3D', desc: { t: 'note', kind: 'none', code: 'CP-3D', title: 'Blocked: ' + WB.moduleName('CP-3D'), sub: 'Module CP-3D', fields: [['Reason', sentence, false]], note: 'Its panels keep this reason; the tables read n/a with it. Open the module for the detail.' } });
      }
      const b = callBar(run, QUESTION_TOOLS(root), notices);
      if (b.lines) {
        const inst = b.find('INSTRUMENT');
        const pl = preferredLine(run);
        if (inst) inst.remove();
        if (pl) {
          const fit = b.find('PORTFOLIO FIT');
          b.lines.insertBefore(pl, fit || null);
        }
      }
      return b.frag;
    };

    // instrument levels and Valuation (with the Recommendation per instrument) beside the yield curve
    const lv = WB.table('snapshot.instrument_levels');
    const rec = WB.table('snapshot.instrument_recommendation');
    let levels;
    if (lv && lv.rows.length) {
      levels = table(lv, { maxRows: lv.rows.length, hide: ['facility_id', 'level_basis', 'bid', 'ask', 'oid', 'metric_basis', 'rationale'] });
      if (rec && rec.rows.length) addColumn(levels, 'Recommendation', (r) => recCell(rec, lv, r), 'The Recommendation table has no row for this instrument.');
    } else levels = WB.conditionLine('Instrument levels are not in this run.');
    const talk = WB.table('cp3.talk_valuation');
    // the talk rows sit behind a disclosure so the spread curve, the page's second first-viewport item, comes up the page
    const talkBox = talk && talk.rows.length
      ? el('details', { class: 'fpa-more' }, [el('summary', { class: 'fpa-more-s' }, [WB.icon('chevron-down', { size: 12, stroke: 1.8 }), el('span', null, 'Talk against comparables'), el('span', { class: 'muted' }, talk.rows.length + ' tranche' + (talk.rows.length === 1 ? '' : 's') + ' at initial talk')]), table(talk, { hide: ['facility_id', 'comparable_basis', 'metric_basis', 'implied_low', 'implied_high'] })])
      : null;
    const levelsBody = [honestNote(), levels, talkBox];
    items.push(item(P({ title: 'Instrument levels and Valuation', tables: ['snapshot.instrument_levels'], anchor: 'fp-levels', body: levelsBody }), 'Instrument levels and Valuation', 'fp-levels', 12, ['CP-3']));

    const obs = WB.table('cp3d.observations');
    const curveBody = [el('div', { class: 'fpa-pad' }, chart(run, 'chart.spread_curve')), blocked && obs && allEmpty(obs) ? el('div', { class: 'fpa-pad' }, WB.conditionLine(reason, { module: 'CP-3D', cls: 'fpa-reason' })) : obs && obs.rows.length ? table(obs, { hide: ['quote_type', 'freshness', 'seniority'], maxRows: 10 }) : null];
    items.push(item(P({ title: 'Spread against maturity', tables: ['cp3d.observations'], anchor: 'fp-curve', body: curveBody }), 'Spread against maturity', 'fp-curve', 12, ['CP-3D']));

    // compensation against risk and security preference, joined by facility
    const comp = WB.table('cp3.compensation');
    const sp = WB.table('cp3.security_preference');
    let prefBody;
    if (comp && comp.rows.length) {
      const fid = (r) => comp.rows[r][col(comp, 'facility_id')];
      const sub2 = (label, node) => el('div', { class: 'fpa-sub' }, [el('span', { class: 'fpa-sub-k' }, label), node]);
      const naChip = (why) => WB.gapChip([], { label: 'n/a', reason: why });
      const instrument = (t, r) => {
        const li = rowOf(lv, 'facility_id', fid(r));
        return { node: el('div', null, [li >= 0 ? WB.renderCell(lv, li, col(lv, 'instrument')).node : WB.renderCell(t, r, col(t, 'facility_id')).node, sub2('Rank: ', WB.renderCell(t, r, col(t, 'structural_rank')).node)]), cls: 'c-text' };
      };
      const prefCell = (t, r) => {
        const si = rowOf(sp, 'facility_id', fid(r));
        return si < 0 ? { node: naChip('The security preference table has no row for this instrument.'), cls: 'c-gap' } : WB.renderCell(sp, si, col(sp, 'preference'));
      };
      const reasonCell = (t, r) => {
        const si = rowOf(sp, 'facility_id', fid(r));
        if (si < 0) return { node: naChip('The security preference table has no row for this instrument.'), cls: 'c-gap' };
        return { node: el('div', null, [WB.renderCell(sp, si, col(sp, 'key_reason')).node, sub2('Watch: ', WB.renderCell(sp, si, col(sp, 'monitoring_trigger')).node)]), cls: 'c-prose' };
      };
      prefBody = [honestNote(), custom(comp, ['facility_id', 'compensation_vs_risk', 'preference', 'recovery_sensitivity', 'key_reason'], { facility_id: instrument, preference: prefCell, key_reason: reasonCell }, { rowHead: true, heads: { facility_id: 'Instrument and structural rank', preference: 'Preference', key_reason: 'Key reason and monitoring trigger' } })];
    } else prefBody = WB.conditionLine('Compensation against risk is not in this run.');
    items.push(item(P({ title: 'Compensation against risk and security preference', tables: ['cp3.compensation', 'cp3.security_preference'], owner: 'CP-3', anchor: 'fp-preference', body: prefBody }), 'Compensation and preference', 'fp-preference', 12, ['CP-3']));

    // market against fundamentals
    const ir = WB.table('cp3d.implied_risk');
    const mvfBody = [
      marketTable(reason),
      ir ? sub('Market-implied default') : null,
      ir ? impliedTable(reason) : null,
    ];
    items.push(item(P({ title: 'Market against fundamentals', tables: ['cp3d.market_vs_fundamental', 'cp3d.implied_risk'], owner: 'CP-3D', anchor: 'fp-market', body: mvfBody }), 'Market against fundamentals', 'fp-market', 12, ['CP-3D']));

    items.push(item(P({ title: 'Peer positioning', tables: ['cp1c.positioning'], anchor: 'fp-peers', body: [el('div', { class: 'fpa-pad' }, chart(run, 'chart.peer_ranges')), table('cp1c.positioning', { hide: ['credit_implication', 'unit_label'] })] }), 'Peer positioning', 'fp-peers', 12, ['CP-1C']));

    items.push(item(P({ title: 'Capital structure', tables: ['snapshot.capital_structure'], owner: 'MODEL', anchor: 'fp-capital', body: capStructure(run), tags: [] }), 'Capital structure', 'fp-capital', 12, ['MODEL']));

    const rvBody = [table('snapshot.relative_value', { maxRows: 16, hide: ['bloomberg_id'] }), el('div', { class: 'fpa-cols fpa-pad' }, [chart(run, 'chart.rv_loan'), chart(run, 'chart.rv_hy')])];
    items.push(item(P({ title: 'Loan and high-yield relative value', tables: ['snapshot.relative_value'], owner: 'CP-3', anchor: 'fp-rv', body: rvBody, collapsed: true }), 'Loan and high-yield relative value', 'fp-rv', 12, ['CP-3']));

    const recS = WB.table('snapshot.recommendation');
    items.push(item(P({ title: 'Recommendation per Strategy and per instrument', tables: ['snapshot.instrument_recommendation'], owner: 'CP-6', anchor: 'fp-recommendation', body: [honestNote(), recS && recS.rows.length ? table(recS, { hide: [] }) : null, sub('Per instrument'), table('snapshot.instrument_recommendation', { hide: ['facility_id'] })] }), 'Recommendation per instrument', 'fp-recommendation', 12, ['CP-6']));

    items.push(item(portfolioFitPanel(run, false), 'Portfolio Fit', 'fp-fit', 12, ['FIT']));

    items.push(item(P({ title: 'Credit view', tables: ['snapshot.credit_view'], owner: 'CP-2', anchor: 'fp-creditview', body: [WB.table('snapshot.credit_view') ? WB.renderKV(WB.table('snapshot.credit_view')) : null, sub('Company profile'), companyKV(run, false)], collapsed: true }), 'Credit view', 'fp-creditview', 12, ['CP-2', 'CP-1A']));

    items.push(notShown(run, 'relative_value.12', 'What changed since the last Report', 'fp-changed', 'CP-8'));
    assemble(canvas, run, barFrag, items);
  }

  WB.registerFrontPage('credit_snapshot', creditSnapshot);
  WB.registerFrontPage('earnings_update', earningsUpdate);
  WB.registerFrontPage('relative_value', relativeValue);
})();
