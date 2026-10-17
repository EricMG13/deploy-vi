/* WB views: Model, Portfolio Fit and the Design system. Registered through the view registry in core.js.
   Everything is built with WB.el; every figure opens a passport through the inspector. */
(function () {
  'use strict';
  const WB = window.WB;
  const el = WB.el;

  /* ---------- shared helpers ---------- */
  const UNIT_WORD = { 'USD millions': 'US$ m', 'USD m': 'US$ m', USD: 'US$' };
  const unitWord = (u) => (u == null ? '' : UNIT_WORD[u] || u);
  const BASIS_WORD = { REPORTED: 'Reported', CALCULATED: 'Calculated', PRO_FORMA: 'Pro forma', PROJECTED: 'Projected', DRIVER: 'Driver' };
  const REASON_SHORT = { NOT_SOURCED: 'n.s.', NOT_APPLICABLE: 'n.a.', NOT_PROJECTED: 'n.p.', COMPONENT_MISSING: 'comp. missing' };
  const REASON_WORDS = { NOT_SOURCED: 'not sourced', NOT_APPLICABLE: 'not applicable', NOT_PROJECTED: 'not projected', COMPONENT_MISSING: 'missing a component' };
  const REASON_LONG = {
    NOT_SOURCED: 'Not sourced: the figure is not in the source documents.',
    NOT_APPLICABLE: 'Not applicable: this line has no meaning for this period.',
    NOT_PROJECTED: 'Not projected: the Model projects only the lines it drives.',
    COMPONENT_MISSING: 'Component missing: a figure this one is calculated from has no value.',
  };
  const modelOf = (run) => (run && run.model) || null;
  const colById = (id) => ((modelOf(WB.run) || {}).columns || []).find((c) => c.column_id === id) || null;
  const lineById = (id) => WB.modelLine(id);
  const num = (v) => {
    const n = Number(v);
    return v != null && v !== '' && Number.isFinite(n) ? n : null;
  };

  /* Model figures: grouped thousands, negatives in parentheses, multiples as 2.34x, never a zero standing in for a gap. */
  function fmtVal(line, v) {
    const n = num(v);
    if (n == null) return String(v);
    let dp;
    if (line && line.unit === 'MULTIPLE') dp = 2;
    else if (line && line.unit === 'PERCENT') dp = 1;
    else if (line && line.unit === 'MONEY') dp = Number.isInteger(n) || Math.abs(n) >= 100 ? 0 : 1;
    else dp = Number.isInteger(n) ? 0 : Math.abs(n) >= 100 ? 0 : 2;
    const s = Math.abs(n).toLocaleString('en-US', { minimumFractionDigits: dp, maximumFractionDigits: dp });
    const zero = Number(s.replace(/,/g, '')) === 0;
    const body = s + (line && line.unit === 'MULTIPLE' ? 'x' : '');
    return n < 0 && !zero ? '(' + body + ')' : body;
  }
  const fmtPlain = (n, dp) => {
    const s = Math.abs(n).toLocaleString('en-US', { minimumFractionDigits: dp, maximumFractionDigits: dp });
    return n < 0 ? '(' + s + ')' : s;
  };

  function citeIsSynthetic(src) {
    const c = WB.citation(src.module, src.citation_id);
    return !!(c && c.synthetic);
  }
  /* One Model cell: the figure kind drawn by shape (cited, synthetic or calculated). */
  function cellKind(cell) {
    if (cell.value == null) return 'gap';
    if (cell.basis === 'REPORTED') return (cell.sources || []).some(citeIsSynthetic) ? 'synthetic' : 'cited';
    return 'calculated';
  }

  /* A passport descriptor that carries a ready passport (used by the house view, EV table and limitations). */
  const ready = (p) => ({ t: 'ready', p });
  const basePassport = WB.buildPassport;
  WB.buildPassport = function (d) {
    if (d && d.t === 'ready') {
      return Object.assign({ kind: 'none', title: '', code: '', sub: '', fields: [], formula: null, inputs: [], excerpt: null, cites: [], usedIn: null, gaps: [], note: '', table: null, chart: null }, d.p);
    }
    const p = basePassport(d);
    if (d && d.t === 'mcell') augmentMcell(p, d);
    return p;
  };

  /* Formula tokens that are Model line ids become labelled input chips that open their own passports. */
  function formulaInputs(line, columnId) {
    const out = [];
    if (!line || !line.formula) return out;
    const seen = new Set();
    for (const tok of String(line.formula).split(/[^A-Za-z0-9_:]+/)) {
      if (!tok || seen.has(tok) || tok === line.line_id) continue;
      const ln = lineById(tok);
      if (!ln) continue;
      seen.add(tok);
      const c = WB.modelCell(tok, columnId);
      const shown = c ? (c.value != null ? fmtVal(ln, c.value) : 'n/a, ' + (REASON_SHORT[c.reason] || c.reason)) : 'no cell';
      out.push({ id: tok, label: ln.label + ' · ' + shown, desc: { t: 'mcell', lineId: tok, columnId } });
    }
    return out;
  }
  function augmentMcell(p, d) {
    const line = lineById(d.lineId);
    const cell = WB.modelCell(d.lineId, d.columnId);
    if (!line || !cell) return;
    const bi = p.fields.findIndex((f) => f[0] === 'Basis');
    if (bi >= 0) p.fields[bi] = ['Basis', BASIS_WORD[cell.basis] || cell.basis || '', false];
    if (cell.value != null) {
      if (cell.stated != null) p.fields.splice(1, 0, ['Stated', String(cell.stated), true]);
      if (cell.stated != null) p.note = ('The stated figure differs from the served one. ' + (p.note || '')).trim();
      const ins = formulaInputs(line, d.columnId);
      if (ins.length) p.inputs = ins.concat(p.kind === 'calculated' ? p.inputs : []);
      if (p.kind === 'calculated' && !line.formula) p.formula = null;
      const srcs = cell.sources || [];
      if (srcs.length) p.excerpt = srcs.map((s) => s.source + ' · ' + s.locator + '\n' + s.excerpt).join('\n\n');
      if (srcs.length > 1) p.fields.push(['Sources', srcs.length + ' in the Model for this cell', false]);
    } else {
      p.fields.push(['Code', cell.reason, true]);
      const bi2 = p.fields.findIndex((f) => f[0] === 'Reason');
      if (bi2 >= 0) p.fields[bi2] = ['Reason', REASON_LONG[cell.reason] || WB.REASONS[cell.reason] || cell.reason, false];
      if (cell.note) p.fields.push(['Detail', cell.note, false]);
    }
  }

  /* scroll helpers inside the canvas */
  function scrollCanvasTo(node) {
    const canvas = document.getElementById('canvas');
    if (!node || !canvas) return;
    const top = node.getBoundingClientRect().top - canvas.getBoundingClientRect().top + canvas.scrollTop - 64;
    canvas.scrollTo({ top: Math.max(0, top) });
  }
  const viewBar = (title, bits) => el('div', { class: 'm-bar' }, el('div', { class: 'm-title' }, [WB.issuerNode({ sep: true }), el('h1', null, title)].concat(bits || [])));
  const sp = () => el('span', { class: 'p-sp' });

  /* =====================================================================
     MODEL
     ===================================================================== */
  const BAND_NAMES = {
    1: 'Operating KPIs',
    2: 'Revenue by business unit',
    3: 'Gross profit',
    4: 'Operating expenses to EBITDA',
    5: 'Adjusted EBITDA and add-backs',
    6: 'Adjusted EBITDA to free cash flow',
    7: 'Net cash flow, cash and liquidity',
    8: 'Debt stack by rank',
    9: 'Debt roll-forward',
    10: 'Interest by facility',
    11: 'Working capital',
    12: 'Credit metrics',
  };
  const GROUPS = [
    { id: 'fy', label: 'Annual actual', test: (c) => c.kind === 'FY', fixed: true },
    { id: 'ytd', label: 'Year to date', toggle: 'Year to date', test: (c) => c.kind === 'PYTD' || c.kind === 'YTD', on: false },
    { id: 'ltm', label: 'Trailing', test: (c) => c.kind === 'LTM', fixed: true },
    { id: 'pf', label: 'Pro forma', toggle: 'PF-LTM', test: (c) => c.kind === 'PF_LTM', on: true },
    { id: 'q', label: 'Quarterly', toggle: 'Quarters', test: (c) => c.kind === 'QUARTER', on: false },
    { id: 'base', label: 'Base case', toggle: 'Base case', test: (c) => c.kind === 'PROJECTED' && c.case === 'BASE', on: false, proj: true },
    { id: 'down', label: 'Downside case', toggle: 'Downside case', test: (c) => c.kind === 'PROJECTED' && c.case === 'DOWNSIDE', on: false, proj: true },
  ];
  const TERM_COLS = [
    { id: 'rank', label: 'Rank' },
    { id: 'pricing', label: 'Pricing' },
    { id: 'floor', label: 'Floor' },
    { id: 'maturity', label: 'Maturity' },
    { id: 'amort', label: 'Amort.' },
  ];
  const LIMIT_TEXT = {
    PROJECTION_OPENING_AT_LTM: 'Projected years open from the LTM position, not from a fiscal year end.',
    MATURITY_NOT_DATED: 'Some debt has no stated maturity, so the maturity wall files it under Undated.',
    PF_EQUALS_LTM: 'The pro forma column equals LTM: no new issue debt is stated.',
  };
  /* each limitation reads by name; its code stays beside it as a secondary chip */
  const LIMIT_TITLE = {
    PROJECTION_OPENING_AT_LTM: 'Projection opens at LTM',
    MATURITY_NOT_DATED: 'Undated maturities',
    PF_EQUALS_LTM: 'Pro forma equals LTM',
  };

  function cellOf(line, columnId) {
    if (!line._cm) line._cm = new Map((line.cells || []).map((c) => [c.column_id, c]));
    return line._cm.get(columnId) || null;
  }
  const snapColumnId = (m) => (m.house && m.house.structuring_ebitda && m.house.structuring_ebitda.column_id) || (m.snapshot_columns && m.snapshot_columns.LTM) || null;

  /* one Model cell as a focusable figure or a compact reason chip */
  function modelCellNode(line, col, rg, hl) {
    const cell = cellOf(line, col.column_id);
    const desc = { t: 'mcell', lineId: line.line_id, columnId: col.column_id };
    if (!cell || cell.value == null) {
      const code = cell ? cell.reason : 'NOT_SOURCED';
      const reason = (REASON_LONG[code] || code) + (cell && cell.note ? ' ' + cell.note : '');
      const chip = WB.gapChip([], { label: cell ? REASON_SHORT[code] || code : 'no cell', reason, desc, rg });
      chip.dataset.mg = line.line_id + '|' + col.column_id;
      return { node: chip, cls: 'mg-null', empty: true };
    }
    const kind = cellKind(cell);
    const shown = fmtVal(line, cell.value);
    const stated = cell.stated != null;
    const b = WB.fig(desc, shown, {
      kind,
      rg,
      label: line.label + ', ' + col.label + ': ' + shown + ', ' + (BASIS_WORD[cell.basis] || '').toLowerCase() + (stated ? ', stated figure differs' : ''),
    });
    b.dataset.mg = line.line_id + '|' + col.column_id;
    return { node: b, cls: 'mg-v' + (col.kind === 'PROJECTED' ? ' is-proj' : '') + (stated ? ' has-stated' : ''), empty: false };
  }

  function termsOf(line) {
    const t = line.terms || {};
    const dash = (v) => (v == null || v === '' ? '—' : String(v));
    const ref = t.reference_rate && t.reference_rate !== '\u2014' ? t.reference_rate : null;
    const pricing = t.spread_or_coupon && ref && !String(t.spread_or_coupon).includes(ref) ? ref + ' + ' + t.spread_or_coupon : dash(t.spread_or_coupon || ref);
    return {
      rank: (line.rank != null ? line.rank + ' · ' : '') + dash(t.seniority),
      pricing,
      floor: dash(t.floor),
      maturity: t.maturity ? WB.fmtDate(t.maturity) : '—',
      amort: dash(t.amortisation),
    };
  }
  function termsPassport(line) {
    const t = line.terms || {};
    const rows = [['Reference rate', t.reference_rate], ['Spread or coupon', t.spread_or_coupon], ['Floor', t.floor], ['Maturity', t.maturity], ['Amortisation', t.amortisation], ['Seniority', t.seniority], ['Secured status', t.secured_status], ['Facility type', t.facility_type]];
    return ready({
      kind: 'none',
      code: line.line_id,
      title: line.label,
      sub: 'Band ' + line.band + ' · Facility terms',
      fields: rows.filter((r) => r[1] != null && r[1] !== '').map((r) => [r[0], String(r[1]), r[0] !== 'Secured status' && r[0] !== 'Facility type']),
      note: 'The Model data carries these terms without a cell-level source. The balance cells on the same row carry their own sources.',
    });
  }

  /* the visible column groups for the current toggles */
  function visibleCols(m, st) {
    const out = [];
    for (const g of GROUPS) {
      if (!g.fixed && !st.groups[g.id]) continue;
      const cols = (m.columns || []).filter(g.test);
      if (cols.length) out.push({ g, cols });
    }
    return out;
  }

  function lineIsEmpty(line, vis) {
    return vis.every((v) => v.cols.every((c) => {
      const cell = cellOf(line, c.column_id);
      return !cell || cell.value == null;
    }));
  }

  function bandGrid(m, lines, st, snapId, idPrefix) {
    const vis = visibleCols(m, st);
    const hasTerms = lines.some((l) => l.terms);
    const showTerms = hasTerms && st.terms;
    const t1 = el('tr', { class: 'mg-g' });
    const t2 = el('tr', { class: 'mg-p' });
    t1.appendChild(el('th', { class: 'mg-corner', rowspan: '2', scope: 'col' }, [el('span', null, 'Line'), el('span', { class: 'mg-cu' }, 'unit')]));
    for (const v of vis) {
      t1.appendChild(el('th', { class: 'mg-gh' + (v.g.proj ? ' is-proj' : ''), colspan: String(v.cols.length), scope: 'colgroup' }, v.g.proj ? [v.g.label, el('span', { class: 'mg-pj' }, 'Projection')] : v.g.label));
      for (const c of v.cols) {
        const label = c.kind === 'PROJECTED' ? c.label.replace(/ (Base|Downside)$/, '') : c.label;
        t2.appendChild(el('th', { class: 'mg-ph' + (c.column_id === snapId ? ' is-snap' : '') + (c.kind === 'PROJECTED' ? ' is-proj' : ''), scope: 'col', title: c.label + ', period end ' + WB.fmtDate(c.end_date) }, label));
      }
    }
    if (showTerms) {
      t1.appendChild(el('th', { class: 'mg-gh', colspan: String(TERM_COLS.length), scope: 'colgroup' }, 'Facility terms'));
      TERM_COLS.forEach((tc) => t2.appendChild(el('th', { class: 'mg-ph mg-th', scope: 'col' }, tc.label)));
    }
    const tbody = el('tbody');
    const shownLines = st.hideEmpty ? lines.filter((l) => !lineIsEmpty(l, vis)) : lines;
    for (const line of shownLines) {
      const kc = (line.kind || 'ACCOUNT').toLowerCase();
      const tr = el('tr', { class: 'mg-r mg-k-' + kc, id: idPrefix + line.line_id, 'data-line': line.line_id });
      const unit = unitWord(line.unit_label);
      tr.appendChild(el('th', { class: 'mg-l', scope: 'row' }, [el('span', { class: 'mg-lt' }, line.label), unit ? el('span', { class: 'mg-lu' }, unit) : null]));
      for (const v of vis) {
        for (const c of v.cols) {
          const r = modelCellNode(line, c, null);
          tr.appendChild(el('td', { class: 'mg-c ' + r.cls + (c.column_id === snapId ? ' is-snap' : '') + (c.kind === 'PROJECTED' ? ' is-projcol' : '') }, r.node));
        }
      }
      if (showTerms) {
        const tv = line.terms ? termsOf(line) : null;
        TERM_COLS.forEach((tc) => {
          const td = el('td', { class: 'mg-t' });
          if (tv) {
            const b = WB.fig(termsPassport(line), el('span', { class: 'fv mg-tv', title: tv[tc.id] }, tv[tc.id]), { kind: 'none', noMark: true, cls: 'fig-term', label: line.label + ', ' + tc.label + ': ' + tv[tc.id] });
            td.appendChild(b);
          }
          tr.appendChild(td);
        });
      }
      tbody.appendChild(tr);
    }
    if (!shownLines.length) tbody.appendChild(el('tr', null, el('td', { class: 'c-empty', colspan: '40' }, 'Every line in this band is empty in the visible columns.')));
    const tbl = el('table', { class: 'mg', 'data-grid': '1' }, [el('caption', { class: 'sr-only' }, 'Model grid'), el('thead', null, [t1, t2]), tbody]);
    WB.initGrid(tbl);
    return el('div', { class: 'mg-scroll tw' }, tbl);
  }

  /* ---------- summary panels ---------- */
  function mFig(lineId, colId, text) {
    const line = lineById(lineId);
    const cell = line && colId ? WB.modelCell(lineId, colId) : null;
    if (!line || !cell) return el('span', { class: 'muted' }, 'not in this Model');
    const r = modelCellNode(line, colById(colId) || { column_id: colId, label: colId, kind: '' }, null);
    if (text && !r.empty) r.node.querySelector('.fv').textContent = text;
    return r.node;
  }
  const kvRow = (label, node, sub) => el('tr', null, [el('th', { scope: 'row', class: 'mv-k' }, [label, sub ? el('span', { class: 'mv-ks' }, sub) : null]), el('td', { class: 'mv-v num' }, node)]);
  const kvTable = (rows, cap) => el('div', { class: 'tw' }, el('table', { class: 'dt mv-kv', 'data-grid': '1' }, [el('caption', { class: 'sr-only' }, cap), el('tbody', null, rows)]));

  /* a figure for a house value: ready passport with formula and input chips */
  function houseFig(title, node, shown, snapId, extraFields) {
    const comps = (node && node.components) || [];
    const inputs = [];
    for (const id of comps) {
      const ln = lineById(id);
      if (!ln) continue;
      const c = WB.modelCell(id, snapId);
      inputs.push({ id, label: ln.label + ' · ' + (c && c.value != null ? fmtVal(ln, c.value) : 'n/a'), desc: { t: 'mcell', lineId: id, columnId: snapId } });
    }
    const col = colById(snapId);
    return WB.fig(
      ready({
        kind: 'calculated',
        code: 'house',
        title,
        sub: 'House view · ' + (col ? col.label : snapId),
        fields: [['Served as', String(node.value), true]].concat(extraFields || []),
        formula: node.formula || null,
        inputs,
        note: 'Computed by the Model on the snapshot column. The house basis is labelled SSIM in the Model data; the owner sets the label.',
      }),
      shown,
      { kind: 'calculated', label: title + ': ' + shown + ', calculated' }
    );
  }
  function houseRow(label, key, fmt, snapId, m, sub) {
    const n = m.house[key];
    if (!n || n.value == null) return kvRow(label, WB.gapChip([], { label: 'n/a', reason: (n && n.reason) || 'The Model produced no value.' }), sub);
    return kvRow(label, houseFig(label, n, fmt(Number(n.value)), snapId), sub);
  }

  function ladderPanel(run, m, snapId) {
    const adj = m.ebitda_adjustments || [];
    const col = colById(snapId);
    const colLabel = col ? col.label : '';
    const rows = [];
    const hasUnreal = adj.some((r) => r.realization_status === 'UNREALIZED');
    const mapLine = (r) => {
      if (/^Reported EBITDA$/i.test(r.line)) return 'ebitda';
      if (/^Structuring EBITDA$/i.test(r.line)) return 'structuring_ebitda';
      if (/^SSIM EBITDA$/i.test(r.line)) return 'adjusted_ebitda';
      const l = (m.lines || []).find((x) => x.band === 5 && x.label === r.line);
      return l ? l.line_id : null;
    };
    adj.forEach((r) => {
      const total = r.kind === 'Total';
      const unreal = r.realization_status === 'UNREALIZED';
      const label = r.line.replace(/SSIM EBITDA/, 'House EBITDA');
      const amt = num(r.amount);
      const lid = mapLine(r);
      const cell = lid ? WB.modelCell(lid, snapId) : null;
      let desc;
      if (cell && cell.value != null && num(cell.value) === amt) desc = { t: 'mcell', lineId: lid, columnId: snapId };
      else desc = ready({ kind: total ? 'calculated' : 'none', code: 'ebitda_adjustments', title: label, sub: colLabel, fields: [['Served as', String(r.amount), true], ['Realisation', r.realization_status === '—' ? '' : r.realization_status, false], ['Basis', r.basis, false]], note: 'From the Model’s EBITDA adjustment register.' });
      const shown = unreal ? fmtPlain(-amt, 0) : fmtPlain(amt, 0);
      const fig = WB.fig(desc, shown, { kind: total || unreal ? 'calculated' : cell ? cellKind(cell) : 'none', label: label + ': ' + shown });
      const prefix = total ? '' : unreal ? '− ' : '+ ';
      const isHouse = /House EBITDA/.test(label);
      rows.push(el('tr', { class: total ? 'mv-tot' : '' }, [
        el('th', { scope: 'row', class: 'mv-k' }, [prefix + label + (total ? ', ' + colLabel : '') + (unreal ? ' (unrealized)' : ''), isHouse ? el('span', { class: 'mv-ks' }, 'Model label: SSIM EBITDA') : null]),
        el('td', { class: 'mv-v num' }, fig),
      ]));
      if (/^Structuring EBITDA$/i.test(r.line) && !hasUnreal) {
        rows.push(kvRow('− Unrealized add-backs', el('span', { class: 'mv-none' }, [WB.icon('emptyset', { size: 12 }), ' none marked']), 'No add-back carries an UNREALIZED status in the Model'));
      }
    });
    if (!adj.length) rows.push(el('tr', null, el('td', { class: 'c-empty', colspan: '2' }, 'No EBITDA adjustments in this Model.')));
    const debtRows = [];
    const tdc = WB.modelCell('total_debt', snapId);
    if (tdc) debtRows.push(kvRow('Total debt (face)', mFig('total_debt', snapId)));
    debtRows.push(houseRow('Adjusted debt', 'adjusted_debt', (n) => fmtPlain(n, 0), snapId, m, 'plus debt-like items'));
    const body = [kvTable(rows, 'House view ladder'), el('h3', { class: 'sub-h' }, 'Debt'), kvTable(debtRows, 'Debt on the snapshot column')];
    return WB.panel({ title: 'House view', anchor: 'house', note: colLabel + ' · ' + unitWord((adj[0] && adj[0].currency === 'USD' ? 'USD' : '') + ' m'), code: 'MODEL', body, tags: [{ kind: 'illustrative', label: 'Illustrative' }].slice(0, 0) });
  }

  function multiplesPanel(run, m, snapId) {
    const metric = (id, label) => (lineById(id) ? kvRow(label, mFig(id, snapId)) : null);
    const metrics = [
      metric('metric:senior_secured_leverage', 'Senior secured leverage'),
      metric('metric:total_leverage_adjusted', 'Total leverage'),
      metric('metric:net_leverage_adjusted', 'Net leverage'),
      metric('metric:interest_coverage_adjusted', 'Interest cover'),
      metric('metric:cash_interest_coverage', 'Cash interest cover, debt only'),
    ].filter(Boolean);
    const x2 = (n) => fmtPlain(n, 2) + 'x';
    const house = [
      houseRow('Structuring multiple', 'structuring_multiple', x2, snapId, m),
      houseRow('House multiple', 'ssim_multiple', x2, snapId, m, 'Model label: SSIM'),
      houseRow('Adjusted leverage', 'adjusted_leverage', x2, snapId, m),
      houseRow('PF interest', 'pf_interest', (n) => fmtPlain(n, 0), snapId, m),
      houseRow('PF interest cover', 'pf_interest_cover', x2, snapId, m),
    ];
    const ev = m.house.ev;
    if (ev && ev.value != null) {
      const mult = ev.inputs && ev.inputs.ssim_ev_multiple;
      house.push(kvRow('Enterprise value', houseFig('Enterprise value', Object.assign({ formula: 'EV multiple x House EBITDA', components: ['adjusted_ebitda'] }, ev), fmtPlain(Number(ev.value), 0), snapId, mult ? [['EV multiple', mult + 'x', true], ['Basis', ev.basis, true]] : []), mult ? 'at ' + fmtPlain(Number(mult), 2) + 'x House EBITDA' : null));
    } else house.push(kvRow('Enterprise value', WB.gapChip([], { label: 'n/a', reason: (ev && ev.reason) || 'The Model produced no EV.' })));
    return WB.panel({ title: 'Multiples and EV', anchor: 'multiples', note: (colById(snapId) || {}).label, code: 'MODEL', body: [metrics.length ? kvTable(metrics, 'Credit multiples on the snapshot column') : null, el('h3', { class: 'sub-h' }, 'House view'), kvTable(house, 'House multiples and EV')] });
  }

  function evPanel(run, m) {
    const cs = m.capital_structure;
    if (!cs || !(cs.rows || []).length) return WB.panel({ title: 'EV and % EV by facility', anchor: 'ev', body: WB.conditionLine('This Model carries no capital structure register.') });
    const colId = cs.column_id;
    const pct = {};
    ((m.house && m.house.pct_ev_by_facility) || []).forEach((p) => (pct[p.facility_id] = p.pct));
    const evv = m.house.ev && m.house.ev.value;
    const head = el('thead', null, el('tr', null, ['Facility', 'Rank', 'Outstanding', 'Maturity', 'Structuring x', 'House x', '% EV'].map((h, i) => el('th', { scope: 'col', class: i >= 2 && i !== 3 ? 'h-numeric' : '' }, h))));
    const tbody = el('tbody');
    cs.rows.forEach((r) => {
      const lineId = 'fac:' + r.facility_id;
      const ln = lineById(lineId);
      const cell = ln ? WB.modelCell(lineId, colId) : null;
      const out = ln && cell && cell.value != null ? modelCellNode(ln, colById(colId) || { column_id: colId, label: colId }, null).node : WB.fig(ready({ kind: 'none', code: r.facility_id, title: r.facility, fields: [['Served as', r.outstanding, true]], note: 'No Model cell carries this balance.' }), WB.fmtNum(r.outstanding), { kind: 'none', noMark: true });
      const mult = (key, title) => WB.fig(ready({ kind: 'calculated', code: r.facility_id, title: title + ': ' + r.facility, sub: r.column_basis, fields: [['Served as', r[key], true]], note: 'Cumulative debt through this facility by payment rank, divided by the EBITDA basis, from the Model’s capital structure register.' }), r[key], { kind: 'calculated', label: title + ', ' + r.facility + ': ' + r[key] });
      const evInputs = [];
      if (ln && cell && cell.value != null) evInputs.push({ id: lineId, label: r.facility + ' · ' + fmtVal(ln, cell.value), desc: { t: 'mcell', lineId, columnId: colId } });
      const pctFig = WB.fig(ready({ kind: 'calculated', code: r.facility_id, title: '% EV: ' + r.facility, sub: r.column_basis, fields: [['Served as', r.pct_ev_pct, true], ['Enterprise value', evv != null ? fmtPlain(Number(evv), 0) : 'not produced', true]], formula: 'outstanding / enterprise value x 100', inputs: evInputs, note: 'Share of the Model’s enterprise value (house EV, see Multiples and EV).' }), r.pct_ev_pct, { kind: 'calculated', label: '% EV, ' + r.facility + ': ' + r.pct_ev_pct });
      tbody.appendChild(el('tr', null, [
        el('th', { scope: 'row', class: 'c-rowh' }, [r.secured === 'Yes' ? el('span', { class: 'mv-lock', title: 'Secured' }, WB.icon('lock', { size: 12, label: 'Secured' })) : null, r.facility]),
        el('td', { class: 'c-text' }, r.rank),
        el('td', { class: 'c-num' }, out),
        el('td', { class: 'c-id' }, r.maturity_date && r.maturity_date !== '—' ? WB.fmtDate(r.maturity_date) : 'Undated'),
        el('td', { class: 'c-num' }, mult('structuring_multiple_x', 'Structuring multiple')),
        el('td', { class: 'c-num' }, mult('ssim_multiple_x', 'House multiple')),
        el('td', { class: 'c-num' }, pctFig),
      ]));
    });
    const tbl = el('table', { class: 'dt', 'data-grid': '1' }, [el('caption', { class: 'sr-only' }, 'EV and % EV by facility'), head, tbody]);
    WB.initGrid(tbl);
    return WB.panel({ title: 'EV and % EV by facility', anchor: 'ev', code: 'MODEL', note: (colById(colId) || {}).label + ' · US$ m', body: el('div', { class: 'tw' }, tbl) });
  }

  function limitationsPanel(run, m, snapId) {
    const items = [];
    const seen = new Set();
    const facilityName = (id) => {
      const row = ((m.capital_structure && m.capital_structure.rows) || []).find((x) => x.facility_id === id);
      const ln = lineById('fac:' + id);
      return (row && row.facility) || (ln && ln.label) || WB.humanize(id);
    };
    (m.limitations || []).forEach((code) => {
      if (seen.has(code)) return;
      seen.add(code);
      let text = LIMIT_TEXT[code] || 'The Model records this limitation without a description in this build.';
      let kind = code === 'PROJECTION_OPENING_AT_LTM' ? 'calculated' : 'gap';
      if (code === 'MATURITY_NOT_DATED') {
        const und = (m.maturity_wall || []).filter((x) => x.fiscal_year === 'Undated');
        if (und.length) text += ' Undated: ' + und.map((u) => facilityName(u.facility_id)).join('; ') + '.';
      }
      items.push({ code, text, kind, label: LIMIT_TITLE[code] || WB.humanize(String(code).toLowerCase()), chip: code });
    });
    const cols = m.columns || [];
    if (!cols.some((c) => c.kind === 'PF_LTM') && !seen.has('PF_EQUALS_LTM')) items.push({ code: 'PF-LTM', text: 'The pack states no new issue debt.', kind: 'gap', label: 'No pro forma column' });
    if (!cols.some((c) => c.kind === 'PROJECTED')) {
      const s = WB.step('CP-2G');
      const why = s && s.status === 'skipped' ? s.reason : 'the Forward Model did not produce a forecast (status: ' + ((m.forecast && m.forecast.status) || 'none') + ')';
      items.push({ code: 'Base / Downside', text: why.charAt(0).toUpperCase() + why.slice(1) + '.', kind: 'gap', label: 'No projected columns' });
    }
    (m.reconciliation_faults || []).forEach((f) => items.push({ code: 'FAULT', text: typeof f === 'string' ? f : JSON.stringify(f), kind: 'gap', label: 'Reconciliation fault' }));
    if (!(m.reconciliation_faults || []).length) items.push({ code: 'RECON', text: 'No reconciliation faults recorded.', kind: 'none', label: 'Reconciliation' });
    // null cells on the snapshot columns, by reason
    const snapIds = Object.values(m.snapshot_columns || {});
    const counts = {};
    let total = 0;
    (m.lines || []).forEach((l) => snapIds.forEach((cid) => {
      const c = cellOf(l, cid);
      if (c && c.value == null) {
        counts[c.reason] = (counts[c.reason] || 0) + 1;
        total++;
      }
    }));
    const list = el('ul', { class: 'mv-lim' }, items.map((it) => {
      const b = WB.fig(ready({ kind: it.kind, code: it.chip || '', title: it.label, sub: 'Model limitation', fields: [['Reading', it.text, false]], note: 'Recorded by the Model (rbot-model/1 limitations, columns and maturity wall).' }), el('span', { class: 'fv' }, [el('strong', null, it.label + '. '), it.text]), { kind: it.kind, label: it.label + ': ' + it.text });
      return el('li', null, [b, it.chip ? el('span', { class: 'mv-lc num', title: 'Code in the Model data' }, it.chip) : null]);
    }));
    const nulls = Object.keys(counts).length
      ? el('p', { class: 'mv-nulls' }, [total + ' snapshot cells are empty: ', Object.keys(counts).map((k, i) => (i ? ', ' : '') + counts[k] + ' ' + (REASON_WORDS[k] || WB.humanize(String(k).toLowerCase()).toLowerCase())).join(''), '. Each cell says why.'])
      : null;
    return WB.panel({ title: 'Model limitations', anchor: 'limitations', code: 'MODEL', body: el('div', { class: 'pad' }, [list, nulls]) });
  }

  function trendsPanel(run) {
    const ids = ['chart.model_strip', 'chart.forecast_lines', 'chart.credit_path', 'chart.maturity_wall', 'chart.adjusted_debt_bridge'];
    const charts = ids.map((id) => (run.charts || []).find((c) => c.chart_id === id)).filter(Boolean);
    const body = el('div', { class: 'mv-charts' }, charts.length ? charts.map((c, i) => el('div', { class: 'mv-ch' + (i === 0 ? ' is-wide' : '') }, WB.chartSlot(c))) : WB.conditionLine('This run has no Model charts.'));
    return WB.panel({ title: 'Credit-metric trends', anchor: 'trends', code: 'MODEL', body });
  }

  /* ---------- the view ---------- */
  function parseAnchor(a, m) {
    if (!a) return null;
    const [lineId, colId] = String(a).split('@');
    if (/^band-\d+$/.test(lineId)) return { band: +lineId.slice(5) };
    if (lineById(lineId)) return { lineId, colId: colId || null };
    return null;
  }

  function renderModel(canvas, run, params) {
    const m = modelOf(run);
    const root = el('div', { class: 'view view-model' });
    canvas.appendChild(root);
    if (!m || !(m.lines || []).length) {
      root.appendChild(viewBar('Model'));
      root.appendChild(WB.conditionLine('This run carries no Model.'));
      WB.setOutline([]);
      return;
    }
    const snapId = snapColumnId(m);
    const st = { groups: {}, terms: true, hideEmpty: false };
    GROUPS.forEach((g) => {
      if (g.toggle) st.groups[g.id] = !!g.on;
    });
    const lineAnchor = parseAnchor(params && params.anchor, m);
    // an arrival on a hidden column opens its group
    let arrivalCol = null;
    if (lineAnchor && lineAnchor.lineId) {
      const snapCol = colById(snapId);
      const wanted = lineAnchor.colId && colById(lineAnchor.colId) ? colById(lineAnchor.colId) : snapCol;
      arrivalCol = wanted;
      const g = wanted && GROUPS.find((x) => x.test(wanted));
      if (g && g.toggle) st.groups[g.id] = true;
    }
    const collapsedBands = new Set();
    const lines = m.lines;
    const bandNos = Array.from(new Set(lines.map((l) => l.band))).sort((a, b) => a - b);

    root.appendChild(viewBar('Model', [el('span', { class: 'm-code num' }, (m.columns || []).length + ' columns · ' + lines.length + ' lines'), el('span', { class: 'm-sub' }, 'Read-only. Every cell opens its basis, sources or formula.'), sp(), WB.collapseTool(() => root)]));

    let arrival = null;
    if (lineAnchor && lineAnchor.lineId) {
      const ln = lineById(lineAnchor.lineId);
      arrival = el('div', { class: 'mv-arrive' }, [WB.icon('arrow-in', { size: 14 }), el('span', null, ['You arrived on ', el('strong', null, ln.label), ' in ', el('strong', null, arrivalCol ? arrivalCol.label : ''), '. Its passport is open on the right.']), sp(), el('button', { type: 'button', class: 'btn-s', onclick: () => history.back() }, [WB.icon('arrow-left', { size: 12 }), 'Back'])]);
      root.appendChild(arrival);
    }

    const summary = el('div', { class: 'mv-summary' });
    summary.appendChild(el('div', { class: 'mv-sum' }, [ladderPanel(run, m, snapId), multiplesPanel(run, m, snapId), limitationsPanel(run, m, snapId)]));
    summary.appendChild(evPanel(run, m));
    summary.appendChild(trendsPanel(run));
    root.appendChild(summary);

    /* column controls */
    const tools = el('div', { class: 'mv-tools', role: 'group', 'aria-label': 'Column groups' });
    const bandsBox = el('div', { class: 'mv-bands' });
    const toggleBtns = [];
    const mkToggle = (label, get, set, tip) => {
      const b = el('button', { type: 'button', class: 'fchip', 'aria-pressed': String(get()), title: tip || label }, label);
      b.addEventListener('click', () => {
        set(!get());
        b.setAttribute('aria-pressed', String(get()));
        b.classList.toggle('on', get());
        paintBands(true);
      });
      b.classList.toggle('on', get());
      return b;
    };
    tools.appendChild(el('span', { class: 'mv-th' }, 'Columns'));
    GROUPS.filter((g) => g.toggle && (m.columns || []).some(g.test)).forEach((g) => {
      const n = (m.columns || []).filter(g.test).length;
      toggleBtns.push(mkToggle(g.toggle + ' (' + n + ')', () => st.groups[g.id], (v) => (st.groups[g.id] = v), g.proj ? 'Projection, not history' : g.toggle));
    });
    if (lines.some((l) => l.terms)) toggleBtns.push(mkToggle('Facility terms', () => st.terms, (v) => (st.terms = v), 'Terms columns on the debt stack'));
    toggleBtns.push(mkToggle('Hide empty lines', () => st.hideEmpty, (v) => (st.hideEmpty = v)));
    toggleBtns.forEach((b) => tools.appendChild(b));
    tools.appendChild(el('span', { class: 'mv-key' }, [el('span', { class: 'mv-key-st' }), ' stated figure differs', el('span', { class: 'mv-key-pj' }, 'Projection'), ' not history']));
    root.appendChild(tools);
    root.appendChild(bandsBox);

    function paintBands(restore) {
      const focus = restore && document.activeElement && document.activeElement.dataset ? document.activeElement.dataset.mg : null;
      const scrolls = {};
      WB.qsa('.panel[data-band]', bandsBox).forEach((p) => {
        const sc = WB.qs('.mg-scroll', p);
        scrolls[p.dataset.band] = sc ? [sc.scrollLeft, sc.scrollTop] : [0, 0];
        if (p.classList.contains('is-collapsed')) collapsedBands.add(p.dataset.band);
        else collapsedBands.delete(p.dataset.band);
      });
      bandsBox.replaceChildren();
      const vis = visibleCols(m, st);
      for (const b of bandNos) {
        const bl = lines.filter((l) => l.band === b);
        const allEmpty = bl.every((l) => lineIsEmpty(l, vis));
        const panel = WB.panel({
          title: 'Band ' + b + ' · ' + (BAND_NAMES[b] || 'Band ' + b),
          anchor: 'band-' + b,
          code: bl.length + ' lines',
          note: allEmpty ? null : null,
          state: allEmpty ? { word: 'No values in these columns', tone: 'neu', icon: 'emptyset' } : null,
          body: bandGrid(m, bl, st, snapId, ''),
          collapsed: collapsedBands.has(String(b)),
        });
        panel.dataset.band = String(b);
        const sc = scrolls[String(b)];
        bandsBox.appendChild(panel);
        const scEl = WB.qs('.mg-scroll', panel);
        if (sc && scEl) {
          scEl.scrollLeft = sc[0];
          scEl.scrollTop = sc[1];
        }
      }
      if (focus) {
        const again = bandsBox.querySelector('[data-mg="' + focus.replace(/"/g, '\\"') + '"]');
        if (again) again.focus({ preventScroll: true });
      }
    }
    paintBands(false);

    WB.setOutline(
      [
        { id: 'p-house', label: 'House view' },
        { id: 'p-multiples', label: 'Multiples and EV' },
        { id: 'p-limitations', label: 'Model limitations' },
        { id: 'p-ev', label: 'EV by facility' },
        { id: 'p-trends', label: 'Credit-metric trends' },
      ].concat(
        bandNos.map((b) => {
          const bl = lines.filter((l) => l.band === b);
          return { id: 'p-band-' + b, label: b + '  ' + (BAND_NAMES[b] || 'Band ' + b), na: bl.every((l) => lineIsEmpty(l, visibleCols(m, st))) };
        })
      )
    );
    WB.page.gapModules = ['CP-1'];

    /* arrival: open the line and column, highlight, show the passport */
    if (lineAnchor && lineAnchor.band) {
      setTimeout(() => scrollCanvasTo(document.getElementById('p-band-' + lineAnchor.band)), 0);
    } else if (lineAnchor && lineAnchor.lineId) {
      setTimeout(() => {
        const key = lineAnchor.lineId + '|' + arrivalCol.column_id;
        const cellEl = bandsBox.querySelector('[data-mg="' + key.replace(/"/g, '\\"') + '"]');
        const row = document.getElementById(lineAnchor.lineId);
        if (!cellEl || !row) return;
        const panel = row.closest('.panel');
        if (panel && panel._setOpen) panel._setOpen(true);
        const sc = row.closest('.mg-scroll');
        if (sc) sc.scrollTop = Math.max(0, row.offsetTop - 80);
        scrollCanvasTo(row);
        row.classList.add('hl');
        cellEl.closest('td').classList.add('is-arrival');
        WB.inspect({ t: 'mcell', lineId: lineAnchor.lineId, columnId: arrivalCol.column_id }, cellEl, { noFocus: true });
      }, 0);
    }
  }

  WB.registerView('model', {
    title: 'Model',
    icon: 'model',
    available: (run) => (run && run.model && (run.model.lines || []).length ? true : 'This run carries no Model.'),
    render: renderModel,
  });
  WB.modelBandGrid = bandGrid;

  /* =====================================================================
     PORTFOLIO FIT
     ===================================================================== */
  const ci = (t, name) => t.columns.indexOf(name);
  const rowsWhere = (t, name, val) => {
    const out = [];
    const c = ci(t, name);
    if (c >= 0) t.rows.forEach((r, i) => r[c] === val && out.push(i));
    return out;
  };

  function limitBars(pid, limitsT, fit, bindingIds) {
    const list = el('ul', { class: 'fl-list' });
    const idx = rowsWhere(limitsT, 'portfolio_id', pid);
    const seen = new Set();
    for (const r of idx) {
      const lid = limitsT.rows[r][ci(limitsT, 'limit_id')];
      if (seen.has(lid)) continue;
      seen.add(lid);
      const g = (n) => limitsT.rows[r][ci(limitsT, n)];
      const cell = (n) => ({ t: 'cell', table: limitsT.id, r, c: ci(limitsT, n) });
      const limit = num(g('limit_value'));
      const cur = num(g('current_value'));
      const status = g('status');
      const isBar = limit != null && cur != null && g('limit_unit') === 'pct_nav';
      // the same rule as the Front Pages (WB.limitState): Within with headroom under 10% of the limit reads Tight
      const ls = isBar ? WB.limitState(status, limit, cur) : WB.limitState(status);
      const tone = ls.tone;
      const icon = ls.icon;
      const unit = isBar ? '% NAV' : '';
      const figOf = (name, text) => WB.fig(cell(name), text, { kind: 'calculated', label: g('parameter') + ', ' + name.replace('_', ' ') + ': ' + text });
      const head = el('div', { class: 'fl-h' }, [
        el('span', { class: 'fl-name' }, g('parameter')),
        el('span', { class: 'fl-id num' }, lid),
        el('span', { class: 'fl-kind' }, [WB.icon(g('limit_kind') === 'Hard' ? 'lock' : 'tag', { size: 11 }), g('limit_kind')]),
        bindingIds.has(lid) ? el('span', { class: 'fl-binds' }, 'Binds an instrument') : null,
        el('span', { class: 'fl-state tone-' + tone }, [WB.icon(icon, { size: 12, stroke: 1.8 }), ls.word]),
      ]);
      // "2.5% NAV", as on the Front Pages
      const withU = (v, ok) => WB.fmtNum(v) + (unit && ok ? '% NAV' : '');
      const parts = [el('span', { class: 'fl-lab' }, 'Limit'), figOf('limit_value', withU(g('limit_value'), true)), el('span', { class: 'fl-lab' }, 'Current'), figOf('current_value', withU(g('current_value'), true)), el('span', { class: 'fl-lab' }, 'Headroom'), figOf('headroom', withU(g('headroom'), num(g('headroom')) != null))];
      const li = el('li', { class: 'fl-row fl-' + tone, id: 'fl-' + WB.cssId(pid + '-' + lid) }, [head]);
      if (isBar) {
        const max = Math.max(limit, cur) || 1;
        li.appendChild(
          el('div', { class: 'fl-bar', role: 'img', 'aria-label': 'Current ' + cur + ' of a ' + limit + ' limit, ' + ls.word }, [
            el('span', { class: 'fl-fill', style: { width: (Math.max(0, cur) / max) * 100 + '%' } }),
            el('span', { class: 'fl-tick', style: { left: (limit / max) * 100 + '%' } }),
          ])
        );
      }
      li.appendChild(el('div', { class: 'fl-v' }, parts));
      if (!isBar) li.appendChild(el('p', { class: 'fl-from' }, 'Stated in the portfolio file; RBOT does not recompute it, so it never binds the maximum size.'));
      list.appendChild(li);
    }
    if (!seen.size) return WB.conditionLine('No limits are recorded for this portfolio.');
    return list;
  }

  function instrumentTable(pid, fitRec, pfT, cp6T) {
    // the size unit sits in the head ("Max size, US$"), so no bare currency trails a figure
    const pr0 = pfT ? pfT.rows.findIndex((r) => r[ci(pfT, 'portfolio_id')] === pid) : -1;
    const sizeUnit = pr0 >= 0 ? WB.unitLabel(pfT.rows[pr0][ci(pfT, 'currency')], pfT.rows[pr0][ci(pfT, 'unit')]) : '';
    // the rating bucket and the limits an instrument touches read under its name, so the verdict and the three calls fit the panel
    const heads = ['Instrument', sizeUnit ? 'Max size, ' + sizeUnit : 'Max size', 'Binding limit', 'Verdict', 'Uncapped', 'Cap', 'Final'];
    const thead = el('thead', null, el('tr', null, heads.map((h, i) => el('th', { scope: 'col', class: i === 1 ? 'h-numeric' : '' }, h))));
    const tbody = el('tbody');
    const names = {};
    (fitRec.inputs.instruments || []).forEach((i) => (names[i.facility_id] = i));
    for (const ins of fitRec.instruments) {
      const meta = names[ins.facility_id] || {};
      const pr = pfT ? pfT.rows.findIndex((r) => r[ci(pfT, 'portfolio_id')] === pid && r[ci(pfT, 'facility_id')] === ins.facility_id) : -1;
      const nm = meta.instrument || (pr >= 0 ? pfT.rows[pr][ci(pfT, 'instrument')] : ins.facility_id);
      const cr = cp6T ? cp6T.rows.findIndex((r) => r[ci(cp6T, 'portfolio_id')] === pid && r[ci(cp6T, 'instrument')] === nm) : -1;
      const tc = (t, r, name) => (t && r >= 0 && ci(t, name) >= 0 ? WB.renderCell(t, r, ci(t, name)) : null);
      const none = (why) => WB.gapChip([], { label: 'n/a', reason: why });
      const td = (c, cls) => el('td', { class: cls || c.cls }, c.node);
      const noRec = 'CP-6 gives no per-portfolio Recommendation for this instrument: only instruments with a level carry one.';
      const touched = el('button', { type: 'button', class: 'fl-chip', title: 'Limits touched: ' + ins.touched.join(', ') + '. Show the limits.', onclick: () => WB.scrollToAnchor('fl-' + WB.cssId(pid + '-' + ins.touched[0])) }, ins.touched.length + ' limits');
      // the cap where CP-6 gives no row: the Fit rule's own output, a calculated figure with its rule as the passport
      const capFig = () => {
        const sg = WB.signal(ins.cap, 'cap');
        return el('td', { class: 'c-scale' }, WB.fig({ t: 'note', kind: 'calculated', code: ins.binding_limit || '', title: 'Cap: ' + nm, sub: 'Portfolio Fit rule', fields: [['Served as', String(ins.cap), true], ['Verdict', String(ins.verdict), false], ['Rule', 'Breaches caps at Avoid, Watch caps at 3 - MW, Fits does not cap.', false]], note: 'Set by the Portfolio Fit rule from the verdict, not by a judgement.' }, el('span', { class: 'fv' }, WB.badge(ins.cap, 'cap')), { kind: 'calculated', cls: 'fig-scale', label: 'Cap ' + sg.word + ', calculated' }));
      };
      const vc = tc(pfT, pr, 'verdict');
      const mc = tc(pfT, pr, 'max_size');
      const un = tc(cp6T, cr, 'uncapped');
      const cp = tc(cp6T, cr, 'cap');
      const fn = tc(cp6T, cr, 'final');
      tbody.appendChild(el('tr', null, [
        el('th', { scope: 'row', class: 'c-rowh' }, [el('span', { class: 'fl-in' }, nm), el('span', { class: 'fl-sub' }, [ins.rating_bucket + (meta.rating ? ' (' + meta.rating + ')' : ''), ' · ', touched])]),
        mc ? el('td', { class: mc.cls }, mc.node) : el('td', { class: 'c-num' }, ins.max_size ? WB.fmtNum(ins.max_size, { group: true }) : none('No maximum size.')),
        el('td', { class: 'c-id' }, ins.binding_limit || '—'),
        vc ? td(vc) : el('td', null, ins.verdict),
        un ? td(un) : el('td', { class: 'c-gap' }, none(noRec)),
        cp ? td(cp) : capFig(),
        fn ? td(fn) : el('td', { class: 'c-gap' }, none(noRec)),
      ]));
    }
    const tbl = el('table', { class: 'dt fl-t', 'data-grid': '1' }, [el('caption', { class: 'sr-only' }, 'Instruments against the limits of this portfolio'), thead, tbody]);
    WB.initGrid(tbl);
    return el('div', { class: 'tw' }, tbl);
  }

  function renderFit(canvas, run) {
    const root = el('div', { class: 'view view-fit' });
    canvas.appendChild(root);
    const fits = run.fit || [];
    root.appendChild(viewBar('Portfolio Fit', [el('span', { class: 'm-code num' }, fits.length + (fits.length === 1 ? ' portfolio' : ' portfolios')), el('span', { class: 'm-sub' }, 'Limits, headroom and the cap the Fit puts on each Recommendation.'), sp(), WB.collapseTool(() => root)]));
    const limitsT = WB.table('fit.limit_headroom');
    const pfT = WB.table('snapshot.portfolio_fit');
    const cp6T = WB.table('cp6.portfolio_recommendation');
    const recT = WB.table('snapshot.recommendation');
    const outline = [];
    fits.forEach((f) => {
      const pj = f.inputs.portfolio;
      const pid = f.portfolio_id;
      const synthetic = /synthetic|fictional/i.test((pj.notes || []).join(' ') + ' ' + pj.portfolio_name);
      const bindingIds = new Set(f.instruments.map((i) => i.binding_limit).filter(Boolean));
      const body = [];
      const cur = WB.unitLabel(pj.currency, pj.unit);
      const cash = (v) => (/^(US\$|€|£)( m| bn)?$/.test(cur) ? cur.replace(/ .*$/, '') + WB.fmtNum(v, { group: true }) + (/ m$/.test(cur) ? 'm' : / bn$/.test(cur) ? 'bn' : '') : WB.fmtNum(v, { group: true }));
      const facts = [['NAV', cash(pj.nav)], ['Par', cash(pj.par)], ['As of', WB.fmtDate(pj.as_of)], ['Strategy', pj.strategy]];
      body.push(el('dl', { class: 'fp-facts' }, facts.flatMap((x) => [el('dt', null, x[0]), el('dd', { class: 'num' }, x[1])])));
      body.push(WB.conditionLine('Proposed trade: the Run Brief states no trade size for this portfolio. The maximum size per instrument below is what the limits allow.'));
      body.push(el('h3', { class: 'sub-h' }, 'Limits and headroom'));
      body.push(limitsT ? limitBars(pid, limitsT, f, bindingIds) : WB.conditionLine('This run carries no limit headroom table.'));
      body.push(el('h3', { class: 'sub-h' }, 'Instruments'));
      body.push(instrumentTable(pid, f, pfT, cp6T));
      if ((pj.notes || []).length) {
        body.push(el('h3', { class: 'sub-h' }, 'Notes'));
        body.push(el('ul', { class: 'fp-notes' }, pj.notes.map((n) => el('li', null, WB.inline(n, 'FIT')))));
      }
      // the per-portfolio Recommendation (CP-6)
      body.push(el('h3', { class: 'sub-h' }, 'CP-6 Recommendation for this portfolio'));
      const finals = cp6T ? rowsWhere(cp6T, 'portfolio_id', pid) : [];
      if (!finals.length) body.push(WB.conditionLine('CP-6 did not run in this Pathway, so there is no per-portfolio Recommendation.'));
      else {
        const digit = (v) => (/^(\d)/.exec(String(v)) || [])[1] || '9';
        let best = finals[0];
        finals.forEach((r) => {
          if (digit(cp6T.rows[r][ci(cp6T, 'final')]) < digit(cp6T.rows[best][ci(cp6T, 'final')])) best = r;
        });
        const strat = recT ? recT.rows.findIndex((r) => r[ci(recT, 'strategy')] === pj.strategy) : -1;
        const items = [];
        if (strat >= 0) {
          const c = WB.renderCell(recT, strat, ci(recT, 'recommendation'));
          items.push(el('div', { class: 'fp-rec' }, [el('span', { class: 'fp-rl' }, pj.strategy + ' Recommendation before the cap'), c.node]));
        }
        const fc = WB.renderCell(cp6T, best, ci(cp6T, 'final'));
        items.push(el('div', { class: 'fp-rec' }, [el('span', { class: 'fp-rl' }, 'Strongest final after the cap: ' + cp6T.rows[best][ci(cp6T, 'instrument')]), fc.node]));
        items.push(el('p', { class: 'fp-rule' }, 'Rule: Breaches caps at Avoid, Watch caps at 3 - MW, Fits does not cap; final is the weaker of the uncapped call and the cap.'));
        body.push(el('div', { class: 'fp-recs' }, items));
      }
      const panel = WB.panel({
        title: pj.portfolio_name,
        anchor: 'fit-' + pid,
        code: null,
        tags: [{ kind: 'text', label: pj.strategy }].concat(synthetic ? [{ kind: 'synthetic', label: 'Synthetic' }] : []),
        note: 'NAV ' + cash(pj.nav) + ' · as of ' + WB.fmtDate(pj.as_of),
        body: el('div', { class: 'pad fp-body' }, body),
      });
      root.appendChild(panel);
      outline.push({ id: panel.id, label: pj.portfolio_name.replace(/ \(fictional\)/, '') });
    });
    // strategies with no portfolio
    const attached = new Set(fits.map((f) => f.inputs.portfolio.strategy));
    const strategies = recT ? Array.from(new Set(recT.rows.map((r) => r[ci(recT, 'strategy')]))) : [];
    const unattached = strategies.filter((s) => !attached.has(s));
    if (unattached.length) root.appendChild(WB.conditionLine(unattached.join(' and ') + (unattached.length === 1 ? ' has' : ' have') + ' no portfolio attached: Fit not run.'));
    WB.setOutline(outline);
    WB.page.gapModules = ['FIT', 'CP-6'];
  }

  WB.registerView('fit', {
    title: 'Portfolio Fit',
    icon: 'fit',
    available: (run) => (run && run.fit && run.fit.length ? true : 'Not in this Pathway'),
    render: renderFit,
  });

  /* =====================================================================
     DESIGN SYSTEM
     ===================================================================== */
  const cssVar = (n) => getComputedStyle(document.documentElement).getPropertyValue(n).trim();
  function lum(hex) {
    const h = hex.replace('#', '');
    const f = h.length === 3 ? h.replace(/./g, (x) => x + x) : h;
    const v = [0, 2, 4].map((i) => parseInt(f.slice(i, i + 2), 16) / 255).map((c) => (c <= 0.03928 ? c / 12.92 : Math.pow((c + 0.055) / 1.055, 2.4)));
    return 0.2126 * v[0] + 0.7152 * v[1] + 0.0722 * v[2];
  }
  function ratio(a, b) {
    const la = lum(a);
    const lb = lum(b);
    return (Math.max(la, lb) + 0.05) / (Math.min(la, lb) + 0.05);
  }
  const isHex = (s) => /^#[0-9a-f]{3,6}$/i.test(s);

  const SWATCHES = [
    ['Brand', [['--navy', 'Frame, verdict bar, ink'], ['--blue', 'Links, focus, selection, issuer series'], ['--blue-hover', 'Hover on blue'], ['--blue-tint', 'Selected rows, chip hover'], ['--blue-row', 'Highlighted row or cell']]],
    ['Neutral', [['--ground', 'Canvas ground'], ['--panel', 'Panels'], ['--rule', 'Rules and borders'], ['--rule-soft', 'Row rules'], ['--ink', 'Primary text'], ['--ink-2', 'Secondary text'], ['--ink-3', 'Tertiary text'], ['--mark-quiet', 'Provenance marks at rest'], ['--hover-row', 'Row hover']]],
    ['Chart', [['--chart-issuer', 'Issuer series'], ['--chart-compare', 'Comparison series'], ['--chart-neutral', 'Context series']]],
  ];
  const PAIRS = [
    ['--ink', '--panel', 4.5, 'Body text on a panel'],
    ['--ink', '--ground', 4.5, 'Body text on the canvas'],
    ['--ink-2', '--panel', 4.5, 'Secondary text on a panel'],
    ['--ink-2', '--ground', 4.5, 'Secondary text on the canvas'],
    ['--ink-3', '--panel', 4.5, 'Tertiary text on a panel'],
    ['--mark-quiet', '--panel', 3, 'Provenance mark at rest (non-text)'],
    ['--blue', '--panel', 4.5, 'Link on a panel'],
    ['--blue', '--blue-row', 4.5, 'Link on a highlighted row'],
    ['--on-navy-2', '--navy', 4.5, 'Secondary text on navy'],
    ['--chart-issuer', '--panel', 3, 'Issuer series on a panel (non-text)'],
    ['--chart-compare', '--panel', 3, 'Comparison series on a panel (non-text)'],
    ['--chart-neutral', '--panel', 3, 'Context series on a panel (non-text)'],
  ];
  const SIGNALS = [
    ['pos', 'Positive', 'Pass, Fits, Headroom, Improving, overweight calls'],
    ['cau', 'Caution', 'With limitations, Watch, Tight, 3 - MW, Medium'],
    ['neg', 'Negative', 'Blocked, Breaches, Deteriorating, underweight calls, High severity'],
    ['neu', 'Neutral', 'N/A, not computable, not run, informational'],
  ];
  const verdict = (r) => el('span', { class: 'ds-pass ' + (r.ok ? 'tone-pos' : 'tone-neg') }, [WB.icon(r.ok ? 'tick' : 'cross', { size: 11, stroke: 2 }), r.ok ? 'passes ' : 'fails ', r.need + ':1']);

  function swatch(name, role) {
    const hex = cssVar(name);
    return el('div', { class: 'ds-sw' }, [el('span', { class: 'ds-chip', style: { background: 'var(' + name + ')' } }), el('span', { class: 'ds-sw-t' }, [el('code', { class: 'num' }, name), el('span', { class: 'num ds-hex' }, hex), el('span', { class: 'ds-role' }, role)])]);
  }
  function contrastTable(pairs) {
    const rows = pairs.map(([fg, bg, need, label]) => {
      const a = cssVar(fg);
      const b = cssVar(bg);
      if (!isHex(a) || !isHex(b)) return el('tr', null, el('td', { colspan: '4' }, label + ': a token is not a hex colour (' + a + ', ' + b + ')'));
      const r = ratio(a, b);
      return el('tr', null, [
        el('th', { scope: 'row', class: 'c-rowh' }, label),
        el('td', { class: 'c-id' }, fg + ' on ' + bg),
        el('td', { class: 'c-num' }, r.toFixed(2) + ':1'),
        el('td', null, verdict({ ok: r >= need, need })),
      ]);
    });
    return el('div', { class: 'tw' }, el('table', { class: 'dt' }, [el('caption', { class: 'sr-only' }, 'Contrast of text and marks on their grounds'), el('thead', null, el('tr', null, ['Pair', 'Tokens', 'Ratio', 'Needs'].map((h, i) => el('th', { scope: 'col', class: i === 2 ? 'h-numeric' : '' }, h)))), el('tbody', null, rows)]));
  }

  /* each specimen: title, the rbot-run/1 fields that fill it, and the live component */
  const spec = (id, title, fields, body, wide) => el('section', { class: 'ds-spec' + (wide ? ' is-wide' : ''), id: 'ds-' + id, 'aria-labelledby': 'ds-' + id + '-h' }, [el('div', { class: 'ds-sh' }, [el('h3', { id: 'ds-' + id + '-h' }, title), fields ? el('p', { class: 'ds-fields' }, [el('span', null, 'Fills from '), el('code', null, fields)]) : null]), el('div', { class: 'ds-sb' }, body)]);

  /* find a real cell (or table) for the specimens */
  function allTables() {
    return Array.from(WB.run._tables.values()).filter((t) => t.id.indexOf('@') < 0 && !/^ds\./.test(t.id));
  }
  /* Specimen search. WB.cellOrigin can throw for a cell shape it does not classify (an odd column in a register table); the specimen search then
     skips that cell. That is a documented fail-open for a design-system sample only: it is counted in window.__wbSpecimenSkips, warned once
     with the count and the first cell, and never added to data-errors (a figure on a real page that throws is an error and is recorded there). */
  window.__wbSpecimenSkips = 0;
  function findCell(pred) {
    let first = null;
    const warn = () => {
      if (window.__wbSpecimenSkips && !window.__wbSpecimenWarned) {
        window.__wbSpecimenWarned = true;
        console.warn('Design system: ' + window.__wbSpecimenSkips + ' cell(s) skipped while picking specimens because WB.cellOrigin threw; the first was ' + first);
      }
    };
    for (const t of allTables()) {
      for (let r = 0; r < Math.min(t.rows.length, 40); r++) {
        for (let c = 0; c < t.columns.length; c++) {
          let o;
          try {
            o = WB.cellOrigin(t, r, c);
          } catch (e) {
            window.__wbSpecimenSkips++;
            if (!first) first = t.id + '[' + r + ',' + c + ']: ' + e.message;
            continue;
          }
          if (pred(o, t, r, c)) {
            warn();
            return { t: 'cell', table: t.id, r, c };
          }
        }
      }
    }
    warn();
    return null;
  }
  function firstMcell(pred) {
    const m = WB.run.model;
    for (const l of m.lines) for (const c of l.cells) if (pred(l, c)) return { t: 'mcell', lineId: l.line_id, columnId: c.column_id };
    return null;
  }

  function passportEl(p) {
    if (typeof WB.renderPassport === 'function') return WB.renderPassport(p);
    const kindWord = WB.originWord[p.kind] || 'No source stated';
    const root = el('div', { class: 'pp pp-' + p.kind });
    root.appendChild(el('div', { class: 'pp-top' }, [WB.mark(p.kind, { size: 12 }), p.code ? el('span', { class: 'pp-code num' }, p.code) : null, el('span', { class: 'pp-kind' }, kindWord.toUpperCase()), p.sub ? el('span', { class: 'pp-sub' }, p.sub) : null]));
    root.appendChild(el('h4', { class: 'pp-title' }, p.title));
    const dl = el('dl', { class: 'pp-f' });
    (p.fields || []).forEach(([l, v, mono]) => v !== '' && v != null && dl.append(el('dt', null, l), el('dd', { class: mono ? 'num wrap' : '' }, v)));
    if (p.formula) dl.append(el('dt', null, 'Formula'), el('dd', null, el('code', { class: 'pp-formula' }, p.formula)));
    root.appendChild(dl);
    const chips = (list) => el('div', { class: 'pp-chips' }, list.map((i) => el('span', { class: 'pchip' }, [WB.mark(i.synthetic ? 'synthetic' : /^C\d+/.test(i.id) ? 'cited' : 'calculated'), el('span', { class: 'pc-id num' }, i.id), el('span', { class: 'pc-l' }, i.label)])));
    if ((p.inputs || []).length) root.append(el('h5', { class: 'pp-h' }, 'Inputs'), chips(p.inputs));
    if (p.excerpt) root.append(el('h5', { class: 'pp-h' }, p.kind === 'synthetic' ? 'TEST DATA rationale' : 'Verbatim excerpt'), el('pre', { class: 'pp-ex' }, p.excerpt));
    if ((p.cites || []).length && !(p.inputs || []).length) root.append(el('h5', { class: 'pp-h' }, 'Cites (' + p.cites.length + ')'), chips(p.cites));
    if (p.note) root.appendChild(el('p', { class: 'pp-note' }, p.note));
    return root;
  }
  const passportSpecimen = (label, desc) => {
    if (!desc) return el('div', { class: 'ds-pp' }, [el('p', { class: 'ds-miss' }, label + ': this run has no figure of this kind.')]);
    const p = WB.buildPassport(desc);
    return el('div', { class: 'ds-pp' }, [el('div', { class: 'ds-pp-l' }, label), passportEl(p)]);
  };

  /* register a specimen table of real rows so passports and gaps resolve */
  function specimenTable(id, base, rowIdx) {
    const key = 'ds.' + id;
    const t = { id: key, owner: base.owner, columns: base.columns.slice(), rows: rowIdx.map((i) => base.rows[i].slice()) };
    WB.run._tables.set(key, t);
    return t;
  }

  function systemSections(run) {
    const secs = [];
    const add = (id, title, body, note) => secs.push({ id, title, body, note });

    /* ----- tokens ----- */
    const colourBody = [];
    SWATCHES.forEach(([g, list]) => colourBody.push(el('h4', { class: 'sub-h' }, g), el('div', { class: 'ds-grid' }, list.map(([n, r]) => swatch(n, r)))));
    colourBody.push(el('h4', { class: 'sub-h' }, 'Contrast on its ground (computed from the tokens)'), contrastTable(PAIRS));
    add('colour', 'Colour tokens', colourBody, 'src/tokens.css');

    const sigBody = [];
    SIGNALS.forEach(([k, name, applies]) => {
      const rows = [
        ['Text on a panel', '--' + k, '--panel', 4.5],
        ['Text on its fill', '--' + k, '--' + k + '-fill', 4.5],
      ];
      if (k !== 'neu') rows.push(['Text on navy', '--' + k + '-on-navy', '--navy', 4.5]);
      sigBody.push(
        el('div', { class: 'ds-sig' }, [
          el('div', { class: 'ds-sig-h' }, [el('span', { class: 'ds-chip', style: { background: 'var(--' + k + ')' } }), el('strong', null, name), el('span', { class: 'ds-role' }, applies)]),
          el('div', { class: 'ds-sig-s' }, [
            el('span', { class: 'chip tone-' + k }, [WB.icon(k === 'pos' ? 'status-pass' : k === 'cau' ? 'status-limited' : k === 'neg' ? 'status-blocked' : 'status-notrun', { size: 13, stroke: 1.8 }), name + ' on its fill']),
            el('span', { class: 'ds-onnavy' }, k === 'neu' ? 'No on-navy variant' : el('span', { class: 'ds-onnavy-s', style: { color: 'var(--' + k + '-on-navy)' } }, name + ' on navy')),
          ]),
          el('div', { class: 'ds-sig-sw' }, [swatch('--' + k, 'Text and marks'), swatch('--' + k + '-fill', 'Fill'), k === 'neu' ? null : swatch('--' + k + '-on-navy', 'On navy')]),
          contrastTable(rows.map((r) => [r[1], r[2], r[3], r[0]])),
        ])
      );
    });
    sigBody.push(el('p', { class: 'ds-rule' }, 'Colour follows credit meaning, not arithmetic sign, and is always paired with an icon, a word or a position marker. Provenance is shape, never a signal colour.'));
    add('signal', 'Signal colours', sigBody, 'src/tokens.css');

    const typeRows = [
      ['Title', '--fs-title', '600 var(--fs-title)/1.25 var(--font-display)', 'Adjusted EBITDA bridge'],
      ['Panel head', '11.5px', '600 11.5px/1.3 var(--font-display)', 'HOUSE VIEW', 'uppercase'],
      ['Body', '--fs-body', '400 var(--fs-body)/1.5 var(--font-text)', 'Leverage is measured on the House EBITDA basis.'],
      ['Label', '--fs-label', '500 var(--fs-label)/1.4 var(--font-text)', 'Facility terms'],
      ['Table text', '--fs-table', '400 var(--fs-table)/1.4 var(--font-text)', 'Senior secured notes due 2032'],
      ['Figure (mono)', '--fs-table', '500 var(--fs-table)/1.4 var(--font-mono)', '0123456789 (1,234.5) 4.68x'],
      ['Column head', '--fs-head', '600 10.5px/1.3 var(--font-text)', 'FY2025', 'uppercase'],
      ['Micro', '--fs-micro', '500 var(--fs-micro)/1.4 var(--font-text)', 'Stated figure differs'],
    ];
    add(
      'type',
      'Type scale',
      el('div', { class: 'tw' }, el('table', { class: 'dt' }, [el('caption', { class: 'sr-only' }, 'Type scale'), el('thead', null, el('tr', null, ['Role', 'Token', 'Sample'].map((h) => el('th', { scope: 'col' }, h)))), el('tbody', null, typeRows.map((r) => el('tr', null, [el('th', { scope: 'row', class: 'c-rowh' }, r[0]), el('td', { class: 'c-id' }, r[1].indexOf('--') === 0 ? r[1] + ' ' + cssVar(r[1]) : r[1]), el('td', null, el('span', { class: 'ds-type', style: { font: r[2], textTransform: r[4] || 'none', letterSpacing: r[4] ? '0.05em' : 'normal' } }, r[3]))]))) ])),
      'src/tokens.css, src/base.css'
    );

    const spaceBody = [
      el('div', { class: 'ds-space' }, ['--s1', '--s2', '--s3', '--s4', '--s5', '--s6'].map((n) => el('div', { class: 'ds-space-r' }, [el('code', { class: 'num' }, n + ' ' + cssVar(n)), el('span', { class: 'ds-bar', style: { width: 'var(' + n + ')' } })]))),
      el('h4', { class: 'sub-h' }, 'Radii'),
      el('div', { class: 'ds-radii' }, [['Panel', '0'], ['--r-chip ' + cssVar('--r-chip'), 'var(--r-chip)'], ['--r-input ' + cssVar('--r-input'), 'var(--r-input)']].map(([l, r]) => el('div', { class: 'ds-rad' }, [el('span', { class: 'ds-rad-b', style: { borderRadius: r } }), el('span', { class: 'num' }, l)]))),
      el('h4', { class: 'sub-h' }, 'Focus'),
      el('div', { class: 'ds-focus-row' }, [el('span', { class: 'ds-focus' }, 'Focus ring: 2px blue, 2px offset'), el('span', { class: 'ds-focus on-navy-bg' }, 'On navy: white')]),
    ];
    add('space', 'Spacing, radii and focus', spaceBody, 'src/tokens.css, src/base.css');

    /* ----- icons ----- */
    add('icons', 'Icon set', el('div', { class: 'ds-icons' }, WB.iconNames.map((n) => el('div', { class: 'ds-ic' }, [WB.icon(n, { size: 16 }), WB.icon(n, { size: 24 }), el('code', { class: 'num' }, n)]))), 'One inline-SVG set: 16px, 1.5px stroke, aria-hidden unless labelled');

    /* ----- components ----- */
    const comps = [];
    const meta = WB.runMeta(run);

    // verdict bars
    const saveHonest = WB.state.honest;
    let illus;
    let honest;
    // the same bar the Front Page draws: title, question, standing, tiles and capped call lines
    const barCfg = (h) => Object.assign(WB.callConfig(run), { title: meta.frontPageName, illustrative: true, meta, stateSwitch: false, honest: h ? 'Honest state: the live CAOS run produced no Recommendation' : null, maxLines: WB.CALL_MAX[run.front_page] || 3, order: WB.CALL_ORDER[run.front_page] || [] });
    try {
      WB.state.honest = false;
      illus = WB.verdictBar(barCfg(false));
      WB.state.honest = true;
      honest = WB.verdictBar(barCfg(true));
    } finally {
      WB.state.honest = saveHonest;
    }
    const blockedId = Object.keys(run.steps || {}).find((k) => WB.stepStatus(k) === 'blocked');
    const blockedReal = !!blockedId;
    const blockedFrom = blockedId || (run.plan || []).find((k) => (WB.step(k) || {}).kind === 'module') || 'CP-1';
    const noticeDesc = (code, title, reading) => ({ t: 'note', kind: 'none', code, title, sub: 'Module ' + code, fields: [['Reading', reading, false]], note: 'A notice tag opens its full sentence here.' });
    const blockedSentence = WB.moduleName(blockedFrom) + ' (' + blockedFrom + ') ' + (blockedReal ? 'is Blocked in this run.' : 'is shown here as the Blocked state: no module is Blocked in this run.');
    // a Blocked module (or a Screening basis) is a tag in the byline row: word, icon, module code; the main risk keeps its call line
    const blockedBar = WB.verdictBar({
      title: meta.issuer.replace(/, Inc\.?$/, '') + ': ' + meta.frontPageName,
      question: WB.moduleQuestion(blockedFrom),
      illustrative: false,
      meta,
      notices: [
        { word: 'Blocked', tone: 'neg', icon: 'status-blocked', code: blockedFrom, desc: noticeDesc(blockedFrom, 'Blocked: ' + WB.moduleName(blockedFrom), blockedSentence) },
        { word: 'Screening basis', tone: 'cau', icon: 'info', code: 'CP-2', desc: noticeDesc('CP-2', 'Screening basis (Quick depth)', 'The Recommendations, Credit Score and Direction rest on a screen, not the full assessment.') },
      ],
      tiles: [{ label: 'Valuation', value: null, reason: blockedReal ? WB.stepReason(blockedId) : 'The module did not produce an accepted result.', producer: blockedFrom }, { label: 'Recommendation', value: null, reason: 'Needs the blocked module’s result.', producer: 'CP-6' }],
      lines: WB.callConfig(run).lines.filter((l) => l.label === 'MAIN RISK'),
    });
    comps.push(
      spec('verdict', 'Verdict bar', 'run_brief snapshot.run_header; pathway; tables snapshot.recommendation, credit_view, instrument_recommendation; step status', [
        el('p', { class: 'ds-cap' }, 'Illustrative: every judgement tile is the module’s view in a design fixture.'),
        el('div', { class: 'ds-vb' }, illus),
        el('p', { class: 'ds-cap' }, 'Real-run state: the tag reads REAL-RUN STATE and every judgement tile the live run did not produce reads Not produced, with the reason and the module. The switch that turns it on sits in the live Front Page\u2019s bar and the state is in the URL (?state=real); these specimens do not carry it.'),
        el('div', { class: 'ds-vb' }, honest),
        el('p', { class: 'ds-cap' }, 'Notices' + (blockedReal ? '' : ' (specimen)') + ': a Blocked module and a Screening basis are tags in the byline row (word, icon, module code); the main risk keeps its call line, the cap folds the other lines.'),
        el('div', { class: 'ds-vb' }, blockedBar),
      ], true)
    );

    // tiles
    const T = (label, key, scale, value, extra) => Object.assign({ label, key, scale, value, illustrative: true }, extra || {});
    const tiles = [
      T('Recommendation', 'recommendation', 'rec', '2 - Modest OW'), T('Recommendation', 'recommendation', 'rec', '3 - MW'), T('Recommendation', 'recommendation', 'rec', '5 - Strong UW'),
      T('CLO', 'recommendation', 'rec', '3 - MW', { cap: { tone: 'neg', icon: 'cross', value: 'Avoid', aria: 'CLO: capped by Fit (specimen).', desc: { t: 'note', kind: 'calculated', code: 'FIT', title: 'Capped by Fit (specimen)', sub: 'Portfolio Fit', fields: [['Rule', 'Breaches caps at Avoid; Watch caps at 3 - MW', false]], note: 'On a Front Page this opens the run\u2019s own portfolio Recommendation row.' } } }),
      T('Valuation', 'valuation', 'val', 'V2 - Attractive'), T('Credit Score', 'credit_score', 'score', '3 - Fair'),
      T('Credit Direction', 'credit_direction', 'dir', 'Improving'), T('Credit Direction', 'credit_direction', 'dir', 'Stable'), T('Credit Direction', 'credit_direction', 'dir', 'Deteriorating'),
      T('Sector Outlook', 'sector_outlook', 'outlook', 'Positive'), T('Distress gate', 'gate', 'gate', 'Not met'), T('Distress gate', 'gate', 'gate', 'Met'),
      T('Covenant tests', 'status', 'cov', 'Tight', { sub: '2 maintenance' }), T('Refinancing pressure', 'pressure', 'press', 'High'), T('Lender protection', 'score', 'five', '2', { word: '2 of 5' }),
      T('Since last Report', 'change', 'plain', 'Deteriorated'), { label: 'Valuation', value: null, reason: 'The Pathway runs no CP-3.', producer: 'CP-3' },
    ];
    comps.push(spec('tiles', 'Position tile, every scale', 'tile {label, key, scale rec|val|score|dir|outlook|gate|cov|press|five|plain, value, ref, illustrative, cap}; value null renders Not produced; cap adds the Capped by Fit badge', el('div', { class: 'verdict ds-tiles' }, el('div', { class: 'v-tiles' }, tiles.map((t) => WB.tile(t)))), true));

    // chips and badges
    const chipRows = el('div', { class: 'ds-row' }, ['pass', 'limitations', 'blocked', 'notrun'].map((s) => WB.statusChip(s)));
    const verdictWords = [['Fits', 'fit_verdict'], ['Watch', 'fit_verdict'], ['Breaches', 'fit_verdict'], ['Headroom', 'status'], ['Tight', 'status'], ['Breached', 'status'], ['Not computable', 'status'], ['Not met', 'status'], ['Unclear', 'status'], ['Met', 'status']];
    comps.push(spec('chips', 'Status and verdict chips', 'steps.<id>.status and qa_status; fit[].instruments[].verdict; cp4.covenant_tests.status; cp4c.distress_gate.status', [chipRows, el('div', { class: 'ds-row' }, verdictWords.map(([w, c]) => WB.badge(w, c)))]));
    const scaleWords = [['1 - Strong OW', 'recommendation'], ['2 - Modest OW', 'recommendation'], ['3 - MW', 'recommendation'], ['4 - Modest UW', 'recommendation'], ['5 - Strong UW', 'recommendation'], ['Avoid', 'recommendation'], ['V1 - Very attractive', 'valuation'], ['V3 - Fair', 'valuation'], ['V5 - Very unattractive', 'valuation'], ['Improving', 'credit_direction'], ['Stable', 'credit_direction'], ['Deteriorating', 'credit_direction'], ['Up', 'trend'], ['Flat', 'trend'], ['Down', 'trend'], ['High', 'severity'], ['Medium', 'severity'], ['Low', 'severity'], ['High', 'confidence'], ['Medium', 'confidence'], ['Low', 'confidence']];
    comps.push(spec('badges', 'Scale and word badges', 'snapshot.recommendation.recommendation; instrument_recommendation.valuation; credit_view.*; severity, pressure and confidence columns (direction per column)', el('div', { class: 'ds-row' }, scaleWords.map(([w, c]) => el('span', { class: 'ds-badge-c' }, [WB.badge(w, c), el('code', { class: 'num' }, c)])))));

    // marks
    const KINDS = ['cited', 'calculated', 'synthetic', 'model', 'gap', 'illustrative', 'none'];
    comps.push(
      spec('marks', 'Provenance marks, quiet and full', 'cite column ([Cn], calc:), citations[].synthetic, model cells basis and sources; scales are illustrative', el('div', { class: 'tw' }, el('table', { class: 'dt' }, [el('caption', { class: 'sr-only' }, 'Provenance marks'), el('thead', null, el('tr', null, ['Kind', 'Quiet (in a table)', 'Full (selected, in a passport)', 'Word'].map((h) => el('th', { scope: 'col' }, h)))), el('tbody', null, KINDS.map((k) => el('tr', null, [el('th', { scope: 'row', class: 'c-rowh' }, k), el('td', null, el('span', { class: 'ds-mq' }, WB.mark(k, { size: 14 }))), el('td', null, el('span', { class: 'pp ds-mf' }, WB.mark(k, { size: 14 }))), el('td', null, WB.originWord[k] || k)])))])))
    );

    // gap chip
    const g1 = WB.gapChip(['G8'], { reason: 'Merger financing is not stated in the sources.' });
    const g2 = WB.gapChip([], { label: 'n.s.', reason: REASON_LONG.NOT_SOURCED });
    const g3 = WB.gapChip([], { label: 'comp. missing', reason: REASON_LONG.COMPONENT_MISSING });
    comps.push(spec('gap', 'Gap chip', 'gaps_md items (G ids); model cells reason NOT_SOURCED, NOT_APPLICABLE, NOT_PROJECTED, COMPONENT_MISSING', el('div', { class: 'ds-row' }, [g1, g2, g3, WB.gapChip([], { label: 'n.a.', reason: REASON_LONG.NOT_APPLICABLE }), WB.gapChip([], { label: 'n.p.', reason: REASON_LONG.NOT_PROJECTED })])));

    // panel
    const pBody = (t) => el('div', { class: 'pad' }, t);
    comps.push(
      spec('panel', 'Panel: open, collapsed, with state', 'front_page_blocks[].title, tables[].owner (code), unit; tags from the table', el('div', { class: 'ds-stack' }, [
        WB.panel({ title: 'Open panel', code: 'CP-1', fig: 'Fig. 1.1', tags: [{ kind: 'illustrative', label: 'Illustrative' }, { kind: 'synthetic', label: 'Synthetic' }], note: 'US$ m', link: { href: '#', label: 'Full analysis' }, body: pBody('A panel is square with a 1px rule and no shadow. Its head carries title, figure number, code, tags and tools.') }),
        WB.panel({ title: 'Collapsed panel', code: 'CP-2', collapsed: true, body: pBody('Hidden until opened.') }),
        WB.panel({ title: 'Blocked module', code: 'CP-3D', state: { word: 'Blocked', tone: 'neg', icon: 'status-blocked' }, body: pBody('The state sits in the head, with its word and icon.') }),
        WB.panel({ title: 'Pinned, never collapses', pinned: true, body: pBody('Key findings do not collapse.') }),
      ]))
    );

    // dense tables
    const cand = allTables().filter((t) => t.columns.indexOf('cite') >= 0 && t.rows.length >= 1);
    const big = cand.slice().sort((a, b) => b.rows.length - a.rows.length)[0];
    const longest = (t) => t.rows.reduce((m, r, i) => Math.max(m, r.reduce((a, v) => Math.max(a, String(v).length), 0)), 0);
    const prose = cand.slice().sort((a, b) => longest(b) - longest(a))[0];
    const gapT = cand.find((t) => t.rows.some((r) => r.some((v) => WB.isEmpty(v)) && r.some((v) => !WB.isEmpty(v))));
    const tableBits = [];
    if (cand.length) {
      const one = specimenTable('one', cand[0], [0]);
      tableBits.push(el('p', { class: 'ds-cap' }, '1 row (' + WB.tableTitle(cand[0].id) + ')'), WB.renderTable(one, { maxRows: 1 }));
      const n20 = Math.min(20, big.rows.length);
      const twenty = specimenTable('twenty', big, Array.from({ length: n20 }, (_, i) => i));
      tableBits.push(el('p', { class: 'ds-cap' }, n20 + ' rows (' + WB.tableTitle(big.id) + '), one tab stop, arrows move between figures'), WB.renderTable(twenty, { maxRows: 20 }));
      const pr = prose.rows.map((r, i) => [r.reduce((a, v) => Math.max(a, String(v).length), 0), i]).sort((a, b) => b[0] - a[0])[0][1];
      tableBits.push(el('p', { class: 'ds-cap' }, 'Long text (' + WB.tableTitle(prose.id) + ')'), WB.renderTable(specimenTable('long', prose, [pr]), { maxRows: 1 }));
      if (gapT) {
        const gi = gapT.rows.findIndex((r) => r.some((v) => WB.isEmpty(v)) && r.some((v) => !WB.isEmpty(v)));
        tableBits.push(el('p', { class: 'ds-cap' }, 'n/a cells (' + WB.tableTitle(gapT.id) + ')'), WB.renderTable(specimenTable('gaps', gapT, [gi]), { maxRows: 1 }));
      }
    } else tableBits.push(WB.conditionLine('This run has no cited tables to show.'));
    const empty = { id: 'ds.empty', owner: cand.length ? cand[0].owner : 'RUN_BRIEF', columns: cand.length ? cand[0].columns.slice() : ['field', 'value'], rows: [] };
    WB.run._tables.set(empty.id, empty);
    tableBits.push(el('p', { class: 'ds-cap' }, 'Empty'), WB.renderTable(empty, { maxRows: 1 }));
    comps.push(spec('table', 'Dense table', 'handoffs.<id>.tables[table_id] {columns, rows}; cite column; currency and unit columns become the unit note', el('div', { class: 'ds-stack' }, tableBits.map((n) => (n.classList && n.classList.contains('tw') ? el('div', { class: 'panel' }, n) : n))), true));

    // kv
    const kvT = allTables().find((t) => t.rows.length === 1 && t.columns.length > 4 && t.columns.length < 18);
    comps.push(spec('kv', 'Key/value table', 'a one-row table, e.g. snapshot.run_header', kvT ? el('div', { class: 'panel' }, WB.renderKV(kvT)) : WB.conditionLine('No one-row table in this run.')));

    // period grid
    const m = run.model;
    const gridBody = [];
    if (m && m.lines && m.lines.length) {
      const lines = m.lines.filter((l) => l.band === 5);
      const allSt = { groups: { ytd: true, pf: true, q: true, base: true, down: true }, terms: true, hideEmpty: false };
      gridBody.push(el('div', { class: 'panel' }, WB.modelBandGrid(m, lines, allSt, snapColumnId(m), 'ds-')));
    } else gridBody.push(WB.conditionLine('This run carries no Model.'));
    comps.push(spec('grid', 'Period grid', 'model.columns[kind, case, label]; model.lines[band, kind, unit, terms, cells{value|reason, basis, stated, note, sources}]', gridBody, true));

    // condition lines
    comps.push(spec('cond', 'Condition line', 'front_page_blocks[].reason and shown:false; steps.<id>.reason', el('div', { class: 'ds-stack' }, [WB.conditionLine('Skipped: this Pathway has no portfolio attached, so Fit is not run.'), WB.conditionLine('What changed is not shown: no Prior Case was accepted at Approval.')])));

    // navigator rows
    const plan = (run.plan || []).filter((id) => (WB.step(id) || {}).kind === 'module');
    const navRow = (status, label, id, n) =>
      el('li', null, el('span', { class: 'nav-row', title: label + ': ' + WB.STATUS_WORD[status] }, [el('span', { class: 'nr-n num' }, String(n)), el('span', { class: 'nr-i tone-' + WB.STATUS_TONE[status] }, WB.icon(WB.STATUS_ICON[status], { size: 14, stroke: 1.8, label: WB.STATUS_WORD[status] })), el('span', { class: 'nr-t' }, label), el('span', { class: 'nr-c num' }, id)]));
    const navRows = ['pass', 'limitations', 'blocked', 'notrun'].map((s, i) => {
      const id = plan.find((k) => WB.stepStatus(k) === s) || (s === 'notrun' ? Object.keys(run.steps || {}).find((k) => WB.stepStatus(k) === 'notrun') : null);
      return navRow(s, id ? WB.moduleName(id) : WB.STATUS_WORD[s] + ' (specimen, none in this run)', id || 'CP-?', i + 1);
    });
    comps.push(spec('nav', 'Navigator rows', 'plan[]; steps.<id>.status, qa_status, reason; modules metadata (plain name)', el('ul', { class: 'nav-modules ds-nav' }, navRows)));

    // passports
    const cited = firstMcell((l, c) => c.value != null && c.basis === 'REPORTED' && (c.sources || []).length && !(c.sources || []).some(citeIsSynthetic));
    const calc = firstMcell((l, c) => c.value != null && l.formula && /\//.test(l.formula) && c.basis !== 'REPORTED' && /^[a-z_:]+( \/ [a-z_]+)$/.test(l.formula) && WB.modelCell(l.formula.split(' / ')[0], c.column_id));
    const synthCell = findCell((o) => o.kind === 'synthetic');
    const gapCell = firstMcell((l, c) => c.value == null);
    const modelCell = findCell((o) => o.kind === 'model');
    const illCell = findCell((o) => o.kind === 'illustrative');
    const noneCell = findCell((o) => o.kind === 'none');
    comps.push(
      spec(
        'passports',
        'Inspector passports',
        'citations[id, source, locator, excerpt, synthetic]; cite column; model cells; gaps_md',
        el('div', { class: 'ds-pps' }, [
          passportSpecimen('Cited', cited),
          passportSpecimen('Calculated, inputs labelled', calc),
          passportSpecimen('Synthetic', synthCell),
          passportSpecimen('Gap', gapCell),
          passportSpecimen('Model-written', modelCell),
          passportSpecimen('Illustrative', illCell),
          passportSpecimen('No source stated', noneCell),
        ]),
        true
      )
    );

    // states
    const stateBox = (title, text) => el('div', { class: 'view view-state ds-state' }, [el('div', { class: 'm-bar' }, el('div', { class: 'm-title' }, el('h1', null, title))), el('div', { class: 'state-body' }, WB.conditionLine(text))]);
    comps.push(spec('states', 'Empty and not-run states', 'steps.<id>.status skipped with reason; unavailable views; declared n/a charts (chart.data.unavailable)', el('div', { class: 'ds-stack' }, [stateBox('Portfolio Fit', 'Not in this Pathway'), stateBox('Module not run', (Object.values(run.steps || {}).find((s) => s.status === 'skipped') || {}).reason || 'This step did not run in this Pathway.'), stateBox('Run not found', 'No run named "x" is embedded in this file.')])));

    add('components', 'Components', comps, 'Rendered live from the same code the views use');

    /* ----- charts ----- */
    const chartBody = [];
    let kinds = null;
    if (typeof WB.chartKinds === 'function') kinds = WB.chartKinds();
    if (!kinds) {
      chartBody.push(WB.conditionLine('WB.chartKinds() is not provided by this build yet. Charts present in this run are shown instead.'));
      kinds = Array.from(new Set((run.charts || []).map((c) => c.kind)));
    }
    const kindName = (k) => (typeof k === 'string' ? k : k.kind || k.name || String(k));
    const grid = el('div', { class: 'ds-charts' });
    kinds.forEach((k) => {
      const kn = kindName(k);
      const ch = (run.charts || []).find((c) => c.kind === kn && !WB.chartUnavailable(c));
      if (ch) grid.appendChild(el('div', { class: 'ds-ch', id: 'ds-chart-' + kn }, [el('h4', { class: 'ds-ch-h' }, [el('code', { class: 'num' }, kn), el('span', null, ' · ' + WB.chartTitle(ch.chart_id))]), WB.chartSlot(ch, { caption: false })]));
      else {
        const other = WB.runIds.find((id) => {
          const r = WB.loadRun(id);
          return r && (r.charts || []).some((c) => c.kind === kn && !WB.chartUnavailable(c));
        });
        grid.appendChild(el('div', { class: 'ds-ch', id: 'ds-chart-' + kn }, [el('h4', { class: 'ds-ch-h' }, el('code', { class: 'num' }, kn)), WB.conditionLine('This run has no ' + kn + ' chart.' + (other ? '' : ' No embedded run has one.')), other ? el('a', { class: 'btn-s', href: WB.href('system', 'ds-chart-' + kn, other) }, ['Open in ' + other, WB.icon('arrow-right', { size: 12 })]) : null]));
      }
    });
    chartBody.push(grid);
    add('charts', 'Chart kinds', chartBody, 'charts[].kind, data {table_id: {columns, rows}}, summary; declared n/a charts render the n/a frame');
    return secs;
  }

  WB.registerView('system', {
    title: 'Design system',
    icon: 'system',
    available: () => true,
    render(canvas, run) {
      const root = el('div', { class: 'view view-system' });
      canvas.appendChild(root);
      root.appendChild(viewBar('Design system', [el('span', { class: 'm-code num' }, 'rbot-run/1'), el('span', { class: 'm-sub' }, 'Tokens, icons and every component in every state, rendered by the code the views use.'), sp(), WB.collapseTool(() => root)]));
      const secs = systemSections(run);
      const outline = [];
      secs.forEach((s) => {
        const p = WB.panel({ title: s.title, anchor: 'ds-' + s.id, note: s.note, body: el('div', { class: 'pad ds-body' }, s.body), collapsible: true });
        root.appendChild(p);
        outline.push({ id: p.id, label: s.title });
        if (s.id === 'components') (s.body || []).forEach((c) => outline.push({ id: c.id, label: ' ' + c.querySelector('h3').textContent }));
      });
      WB.setOutline(outline);
      WB.page.gapModules = [];
    },
  });
})();
