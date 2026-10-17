/* WB pages: the views this foundation registers: front (generic), module/<id>, evidence, limitations.
   Later agents register model, fit, system and replace the generic Front Page with bespoke compositions. */
(function () {
  'use strict';
  const WB = window.WB;
  const el = WB.el;

  /* ---------- the call: a verdict bar built from the run ---------- */
  const strategyRows = () => {
    const t = WB.table('snapshot.recommendation');
    return t ? t : null;
  };
  function cellRef(table, r, name) {
    const c = table.columns.indexOf(name);
    return { t: 'cell', table: table.id, r, c };
  }
  function pickRow(table, col, val) {
    const c = table.columns.indexOf(col);
    return c < 0 ? -1 : table.rows.findIndex((row) => row[c] === val);
  }
  function digit(v) {
    const m = /^V?(\d)/.exec(String(v));
    return m ? +m[1] : 99;
  }
  /* best instrument: lowest Recommendation number among instrument_recommendation rows */
  function bestInstrument() {
    const t = WB.table('snapshot.instrument_recommendation');
    if (!t || !t.rows.length) return null;
    const ri = t.columns.indexOf('recommendation');
    let best = -1;
    let bestD = 99;
    t.rows.forEach((row, i) => {
      const d = digit(row[ri]);
      if (d < bestD) {
        bestD = d;
        best = i;
      }
    });
    return best < 0 ? null : { table: t, r: best };
  }
  const HONEST = {
    rec: { reason: 'CP-6 never ran in the live CAOS run, so no Recommendation exists.', short: 'CP-6 did not run live', producer: 'CP-6' },
    valuation: { reason: 'The live CAOS run returned Requires More Work for CP-3: no Valuation.', short: 'CP-3: Requires More Work', producer: 'CP-3' },
    score: { reason: 'The live CP-3 fundamental score is Not Scorable: no factor weights were supplied.', short: 'CP-3: Not Scorable', producer: 'CP-3' },
  };
  const NO_CP6 = 'This Pathway runs no CP-6, so it produces no Recommendation.';
  const NO_CP3 = 'This Pathway runs no CP-3, so it produces no Valuation.';
  /* call lines in the order each Front Page's content doc gives them; the bar shows the first three (the main risk always among them, see
     WB.CALL_RESERVED), the rest sit behind a disclosure. A Blocked module, a Screening basis and (Covenant) what the Pathway does not run are tags in the byline row, not call lines. */
  WB.CALL_ORDER = {
    credit_snapshot: ['MAIN RISK', 'RELATIVE VALUE', 'PORTFOLIO FIT', 'INSTRUMENT'],
    earnings_update: ['THE QUARTER', 'MAIN RISK', 'NO RECOMMENDATION', 'WATCH'],
    relative_value: ['PREFERRED', 'RELATIVE VALUE', 'PORTFOLIO FIT', 'MAIN RISK', 'INSTRUMENT'],
    covenant_refinancing: ['COVENANTS', 'LIQUIDITY', 'MAIN RISK', 'NEW TRANCHES'],
    distressed_restructuring: ['FULCRUM', 'MAIN RISK', 'INSTRUMENT', 'PORTFOLIO FIT', 'GATE', 'LIQUIDITY'],
    portfolio_decision: ['PORTFOLIO FIT', 'INSTRUMENT', 'MAIN RISK'],
  };
  // Covenant's call is four facts; the Distressed bar shows its fulcrum and the main risk (the gate is a tile), the rest sit behind the disclosure
  WB.CALL_MAX = { covenant_refinancing: 4, distressed_restructuring: 2 };

  function mkTile(label, key, scale, table, r, col, miss, honest) {
    if (honest && !WB.state.honest) honest = null;
    if (WB.state.honest && honest) return { label, key, scale, value: null, reason: honest.reason, short: honest.short, producer: honest.producer };
    if (!table || r < 0 || r == null) return { label, key, scale, value: null, reason: miss.reason, short: miss.short, producer: miss.producer };
    const v = WB.cellValue(table, r, col);
    if (WB.isEmpty(v)) return { label, key, scale, value: null, reason: miss.reason, short: miss.short, producer: miss.producer };
    const o = WB.cellOrigin(table, r, table.columns.indexOf(col));
    return { label, key, scale, value: v, ref: cellRef(table, r, col), illustrative: o.kind === 'illustrative' };
  }
  function worstOf(values, order) {
    let w = null;
    for (const v of values) if (order.indexOf(v) > (w == null ? -1 : order.indexOf(w))) w = v;
    return w;
  }
  WB.callConfig = function (run) {
    const meta = WB.runMeta(run);
    const fp = run.front_page;
    const honest = WB.state.honest;
    const cv = WB.table('snapshot.credit_view');
    const rec = strategyRows();
    const tiles = [];
    const lines = [];
    const strategyTiles = () => {
      for (const s of ['CLO', 'Indexed Loans', 'Indexed HY']) {
        const r = rec ? pickRow(rec, 'strategy', s) : -1;
        tiles.push(mkTile(s === 'CLO' ? 'CLO' : s, 'recommendation', 'rec', rec, r, 'recommendation', { reason: NO_CP6, short: 'CP-6 not in this Pathway', producer: 'CP-6' }, HONEST.rec));
      }
    };
    const valuationTile = () => {
      const b = bestInstrument();
      tiles.push(mkTile('Valuation', 'valuation', 'val', b && b.table, b ? b.r : -1, 'valuation', { reason: NO_CP3, short: 'CP-3 not in this Pathway', producer: 'CP-3' }, HONEST.valuation));
    };
    const cvTile = (label, key, scale, col, honestKey) => {
      tiles.push(mkTile(label, key, scale, cv, cv && cv.rows.length ? 0 : -1, col, { reason: 'No credit view in this run.', short: 'No credit view', producer: 'CP-2' }, honestKey));
    };
    if (fp === 'credit_snapshot' || fp === 'relative_value') {
      strategyTiles();
      valuationTile();
      cvTile('Credit Score', 'credit_score', 'score', 'credit_score', HONEST.score);
      cvTile('Credit Direction', 'credit_direction', 'dir', 'credit_direction');
    } else if (fp === 'earnings_update') {
      cvTile('Credit Score', 'credit_score', 'score', 'credit_score', HONEST.score);
      cvTile('Credit Direction', 'credit_direction', 'dir', 'credit_direction');
      cvTile('Sector Outlook', 'sector_outlook', 'outlook', 'sector_outlook');
      const wc = WB.table('cp8.what_changed');
      const r = wc ? pickRow(wc, 'field', 'Credit Direction') : -1;
      tiles.push(mkTile('Since last Report', 'change', 'plain', wc, r, 'change', { reason: 'No Prior Case was accepted at Approval, so the page cannot say what changed.', producer: 'CP-8' }));
      const cp = WB.table('snapshot.company_profile');
      tiles.push(mkTile('Sponsor Quality', 'sponsor_quality', 'plain', cp, cp && cp.rows.length ? 0 : -1, 'sponsor_quality', { reason: 'No company profile in this run.', producer: 'CP-1A' }));
      // content doc 02: the absent Recommendation is stated as a call line (NO RECOMMENDATION), not as a tile
    } else if (fp === 'covenant_refinancing') {
      cvTile('Credit Score', 'credit_score', 'score', 'credit_score', HONEST.score);
      const ct = WB.table('cp4.covenant_tests');
      if (ct && ct.rows.length) {
        const si = ct.columns.indexOf('status');
        const w = worstOf(ct.rows.map((r) => r[si]), ['Headroom', 'Not computable', 'Tight', 'Breached']);
        const wr = ct.rows.findIndex((r) => r[si] === w);
        const maint = ct.rows.filter((r) => r[ct.columns.indexOf('test_type')] === 'Maintenance').length;
        tiles.push({ label: 'Covenant tests', key: 'status', scale: 'cov', value: w, ref: cellRef(ct, wr, 'status'), illustrative: false, sub: maint + ' maintenance' });
      } else tiles.push({ label: 'Covenant tests', value: null, reason: 'No covenant tests in this run.', producer: 'CP-4' });
      const ps = WB.table('cp4.protection_score');
      if (ps && ps.rows.length) {
        const si = ps.columns.indexOf('score');
        let br = 0;
        ps.rows.forEach((r, i) => {
          if (+r[si] < +ps.rows[br][si]) br = i;
        });
        tiles.push({ label: 'Lender protection', key: 'score', scale: 'five', value: ps.rows[br][si], word: ps.rows[br][si] + ' of 5', ref: cellRef(ps, br, 'score'), illustrative: true });
      } else tiles.push({ label: 'Lender protection', value: null, reason: 'No protection score in this run.', producer: 'CP-4' });
      const mp = WB.table('cp3c.maturity_pressure');
      if (mp && mp.rows.length) {
        const pi = mp.columns.indexOf('pressure');
        const w = worstOf(mp.rows.map((r) => r[pi]), ['Low', 'Medium', 'High']);
        const wr = mp.rows.findIndex((r) => r[pi] === w);
        tiles.push({ label: 'Refinancing pressure', key: 'pressure', scale: 'press', value: w, ref: cellRef(mp, wr, 'pressure'), illustrative: true });
      } else tiles.push({ label: 'Refinancing pressure', value: null, reason: 'No maturity pressure table in this run.', producer: 'CP-3C' });
      cvTile('Credit Direction', 'credit_direction', 'dir', 'credit_direction');
    } else if (fp === 'distressed_restructuring') {
      const dg = WB.table('cp4c.distress_gate');
      if (honest) tiles.push({ label: 'Distress gate', key: 'gate', scale: 'gate', value: 'Not met', ref: { t: 'note', kind: 'cited', code: 'CAOS CP-4C', title: 'Distress gate: Not met', sub: 'Real run outcome', fields: [['Served as', 'Not Applicable: no named distress trigger', false]], note: 'The live CAOS CP-4C run found no named distress trigger and returned Not Applicable.' }, illustrative: false });
      else if (dg && dg.rows.length) {
        const si = dg.columns.indexOf('status');
        const r = dg.rows.length - 1;
        tiles.push({ label: 'Distress gate', key: 'gate', scale: 'gate', value: dg.rows[r][si], ref: cellRef(dg, r, 'status'), illustrative: true });
      } else tiles.push({ label: 'Distress gate', value: null, reason: 'No distress gate in this run.', producer: 'CP-4C' });
      strategyTiles();
      cvTile('Credit Score', 'credit_score', 'score', 'credit_score', HONEST.score);
    } else if (fp === 'portfolio_decision') {
      strategyTiles();
      const pr = WB.table('cp6.portfolio_recommendation');
      if (pr && pr.rows.length) {
        const pidx = pr.columns.indexOf('portfolio_id');
        const fi = pr.columns.indexOf('final');
        const seen = new Set();
        for (let r = 0; r < pr.rows.length; r++) {
          const pid = pr.rows[r][pidx];
          if (seen.has(pid)) continue;
          seen.add(pid);
          let best = r;
          pr.rows.forEach((row, i) => {
            if (row[pidx] === pid && digit(row[fi]) < digit(pr.rows[best][fi])) best = i;
          });
          const name = (WB.table('cp0.portfolios') && WB.cellValue(WB.table('cp0.portfolios'), pickRow(WB.table('cp0.portfolios'), 'portfolio_id', pid), 'portfolio_name')) || pid;
          tiles.push(mkTile(String(name).replace(/ Ltd.*$/, '') + ' final', 'final', 'rec', pr, best, 'final', { reason: 'No portfolio Recommendation in this run.', short: 'No portfolio Recommendation', producer: 'CP-6' }, HONEST.rec));
        }
      }
      valuationTile();
      cvTile('Credit Score', 'credit_score', 'score', 'credit_score', HONEST.score);
    }

    /* call lines */
    if (cv && cv.rows.length && cv.columns.indexOf('primary_downside') >= 0) {
      lines.push({ label: 'MAIN RISK', tone: 'neg', children: WB.inline(WB.cellValue(cv, 0, 'primary_downside'), WB.citeModule(cv.owner)) });
    }
    if (honest && (fp === 'credit_snapshot' || fp === 'relative_value')) {
      lines.push({ label: 'RELATIVE VALUE', tone: 'cau', children: 'Unclear. The live CAOS CP-3 says Requires More Work for both priced 2032 bonds; no security is Preferred.' });
    }
    const fitLine = () => {
      const pf = WB.table('snapshot.portfolio_fit');
      if (!pf || !pf.rows.length) {
        lines.push({ label: 'PORTFOLIO FIT', tone: 'neu', children: 'Not run: this Pathway attaches no portfolio, so there is no Fit verdict.' });
        return;
      }
      const pid = pf.columns.indexOf('portfolio_id');
      const vi = pf.columns.indexOf('verdict');
      const seen = [];
      pf.rows.forEach((r) => {
        if (!seen.includes(r[pid])) seen.push(r[pid]);
      });
      const kids = [];
      seen.forEach((p) => {
        const rows = pf.rows.filter((r) => r[pid] === p);
        const fit = (run.fit || []).find((f) => f.portfolio_id === p);
        const pj = fit && fit.inputs && fit.inputs.portfolio;
        const name = (pj && pj.portfolio_name) || p;
        const syn = pj && /synthetic|fictional/i.test((pj.notes || []).join(' '));
        kids.push(el('b', null, String(name).replace(/ Ltd.*$/, '')), ' ', syn ? el('span', { class: 'v-syn' }, 'SYNTHETIC') : null, ' ');
        ['Fits', 'Watch', 'Breaches'].forEach((v) => {
          const n = rows.filter((r) => r[vi] === v).length;
          if (!n) return;
          const sg = WB.signal(v);
          const first = pf.rows.indexOf(rows.find((r) => r[vi] === v));
          kids.push(el('button', { type: 'button', class: 'v-verdict tone-' + sg.tone, 'data-ref': WB.ref(cellRef(pf, first, 'verdict')) }, [WB.icon(sg.icon, { size: 11, stroke: 2 }), n + ' ' + v]), ' ');
        });
        kids.push(el('a', { class: 'v-lnk', href: WB.href(WB.views.fit ? 'fit' : 'module/FIT', null) }, 'Details'), '. ');
      });
      lines.push({ label: 'PORTFOLIO FIT', tone: 'neu', children: kids });
    };
    if (fp !== 'earnings_update') fitLine();
    const bi = bestInstrument();
    if (bi && !honest && fp !== 'earnings_update' && fp !== 'covenant_refinancing') {
      const t = bi.table;
      const rv = WB.cellValue(t, bi.r, 'recommendation');
      const kids = [el('b', null, WB.cellValue(t, bi.r, 'instrument')), ': ' + rv + ', ' + WB.cellValue(t, bi.r, 'valuation') + '. '];
      kids.push(WB.inline(WB.cellValue(t, bi.r, 'rationale'), WB.citeModule(t.owner)));
      lines.push({ label: 'INSTRUMENT', tone: 'neu', children: kids });
    }
    if (fp === 'earnings_update') {
      const hp = WB.table('snapshot.historical_performance');
      if (hp && hp.rows.length) lines.push({ label: 'THE QUARTER', tone: 'neu', children: WB.inline(WB.cellValue(hp, 0, 'text'), WB.citeModule(hp.owner)) });
    }
    if (fp === 'distressed_restructuring') {
      const rc = WB.table('cp4c.recoveries');
      if (rc && rc.rows.length) {
        const fi = rc.columns.indexOf('fulcrum');
        const si = rc.columns.indexOf('scenario');
        const ci = rc.columns.indexOf('class_id');
        const f = rc.rows.filter((r) => r[fi] === 'Yes').map((r) => WB.claimName(r[ci]) + ' (' + String(r[si]).replace(/: /, ', ') + ')');
        lines.push({ label: 'FULCRUM', tone: 'neg', children: f.length ? f.join('; ') : 'No fulcrum class in the scenarios shown.' });
      }
    }
    return { tiles, lines, meta };
  };
  WB.callBar = function (run, extra, notices) {
    const cfg = WB.callConfig(run);
    const meta = cfg.meta;
    const fpName = meta.frontPageName;
    const questions = {
      credit_snapshot: 'Should we own this issuer, in which instrument, and why?',
      earnings_update: 'What did the period change, and does the credit view move?',
      relative_value: 'Which instrument is best compensated for its risk, and at what level?',
      covenant_refinancing: 'Which provisions protect creditors, and can the issuer refinance?',
      distressed_restructuring: 'Is the distress gate met, which path and fulcrum are most credible, and what recoveries follow?',
      portfolio_decision: 'Should each portfolio own it, how much, and which instrument?',
    };
    const tools = el('span', { class: 'v-tools' }, extra || null);
    return WB.verdictBar({
      title: fpName,
      question: questions[run.front_page] || '',
      illustrative: true,
      bylineNodes: WB.bylineNodes(meta),
      notices: notices || [],
      tiles: cfg.tiles,
      lines: cfg.lines,
      honest: WB.state.honest ? 'Honest state: the live CAOS run produced no Recommendation' : null,
      tools,
      maxLines: WB.CALL_MAX[run.front_page] || 3,
      order: WB.CALL_ORDER[run.front_page] || [],
    });
  };
  function fmtDate(iso) {
    const m = /^(\d{4})-(\d{2})-(\d{2})$/.exec(iso || '');
    if (!m) return iso || '';
    const mo = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'][+m[2] - 1];
    return +m[3] + ' ' + mo + ' ' + m[1];
  }
  WB.fmtDate = fmtDate;

  /* ---------- Front Page (generic) ---------- */
  /* A short, unique panel title from a block title ("Chart: maturity wall" gives "Maturity wall"; a repeated lead keeps its qualifier). */
  /* "What changed since ⟨date⟩": the placeholder names the Prior Case Report's date when there is one, else "the last Report" */
  WB.fillTitle = function (title) {
    const pc = (WB.run && WB.run.prior_case) || {};
    return String(title).replace(/⟨date⟩/g, pc.report_date ? fmtDate(pc.report_date) : 'the last Report');
  };
  WB.blockTitles = function (blocks) {
    const seen = new Set();
    return blocks.map((b) => {
      let t = WB.fillTitle(String(b.title)).split(/[(;]/)[0].trim();
      t = t.replace(/^Chart: /, '');
      t = t.charAt(0).toUpperCase() + t.slice(1);
      let short = t.split(':')[0].trim();
      if (seen.has(short)) short = t.length > 64 ? t.slice(0, 61).replace(/[,\s]+$/, '') + '...' : t;
      seen.add(short);
      return short;
    });
  };
  WB.blockTitle = (b) => WB.fillTitle(String(b.title)).split(/[:(;]/)[0].trim();
  WB.genericFrontPage = function (canvas, run) {
    const root = el('div', { class: 'view view-front' });
    canvas.appendChild(root);
    const tools = WB.collapseTool(() => root);
    root.appendChild(WB.callBar(run, tools));
    const blocks = run.front_page_blocks || [];
    const grid = el('div', { class: 'fp-grid' });
    const outline = [];
    const half = [];
    const panels = [];
    const titles = WB.blockTitles(blocks);
    blocks.forEach((b, bi) => {
      const n = +String(b.id).split('.').pop();
      const title = titles[bi];
      outline.push({ id: 'p-' + WB.cssId(b.id), label: title, na: !b.shown });
      if (!b.shown) {
        const reason = b.reason ? 'Not shown: ' + b.reason + '.' : 'Not shown.';
        panels.push({ node: WB.panel({ title, code: 'CP-8', anchor: b.id, collapsible: false, className: 'panel-cond', note: reason, body: null }), span: 12 });
        return;
      }
      const tables = (b.tables || []).map((tid) => ({ tid, table: WB.table(tid) }));
      const charts = WB.chartsForBlock(n);
      const body = [];
      let weight = 0;
      tables.forEach(({ tid, table }) => {
        if (!table) {
          body.push(WB.conditionLine('Table ' + tid + ' is not in this run.'));
          return;
        }
        weight += table.rows.length;
        const kv = table.rows.length === 1 && table.columns.length > 3;
        if (tables.length > 1) body.push(el('h3', { class: 'sub-h' }, WB.tableTitle(tid)));
        body.push(kv ? WB.renderKV(table) : WB.renderTable(table, { anchor: tid, maxRows: 12 }));
      });
      charts.forEach((c) => {
        weight += 12;
        body.push(WB.chartSlot(c));
      });
      const firstOwner = (tables.find((x) => x.table) || {}).table;
      const owner = firstOwner ? firstOwner.owner : null;
      const tags = [];
      tables.forEach(({ table }) => table && WB.tableTags(table).forEach((t) => !tags.find((x) => x.kind === t.kind) && tags.push(t)));
      const blocked = tables.some(({ table }) => table && table.owner !== 'RUN_BRIEF' && WB.stepStatus(table.owner) === 'blocked');
      const node = WB.panel({
        title,
        code: owner === 'RUN_BRIEF' ? 'BRIEF' : owner,
        state: blocked ? { word: 'Blocked', tone: 'neg', icon: 'status-blocked' } : null,
        tags,
        anchor: b.id,
        link: owner && WB.ownerHref(owner) ? { href: WB.ownerHref(owner), label: 'Full analysis' } : null,
        body,
      });
      const halfOk = tables.length === 1 && tables[0].table && charts.length === 0 && (() => {
        const t = tables[0].table;
        if (t.rows.length === 1 && t.columns.length > 3) return true;
        const ks = WB.columnKinds(t).filter((k) => k.kind !== 'hidden');
        return ks.length <= 4 && !ks.some((k) => k.kind === 'prose') && t.rows.length <= 10;
      })();
      panels.push({ node, span: halfOk ? 6 : 12 });
    });
    // pair consecutive half-width panels; an unpaired one goes full width
    for (let i = 0; i < panels.length; i++) {
      const p = panels[i];
      if (p.span === 6) {
        const nxt = panels[i + 1];
        if (nxt && nxt.span === 6) {
          nxt.paired = true;
          half.push(i);
        } else p.span = 12;
      }
    }
    panels.forEach((p) => {
      p.node.style.gridColumn = 'span ' + p.span;
      grid.appendChild(p.node);
    });
    root.appendChild(grid);
    WB.setOutline(outline);
    WB.page.gapModules = Array.from(new Set(blocks.filter((b) => b.shown).flatMap((b) => (b.tables || []).map((t) => WB.tableOwner(t)).filter(Boolean).map((o) => WB.citeModule(o)))));
  };
  WB.registerView('front', {
    title: 'Front Page',
    icon: 'frontpage',
    available: () => true,
    render(canvas, run, params) {
      // every Front Page states Illustrative once, in its verdict bar: its panels then drop the Illustrative tag (WB.panel)
      WB.page.basis = 'illustrative';
      const custom = WB.frontPages[run.front_page];
      if (custom) return custom(canvas, run, params);
      return WB.genericFrontPage(canvas, run, params);
    },
  });

  /* ---------- module view (frame 05) ---------- */
  function stepNeighbours(id) {
    const plan = WB.run.plan || [];
    const i = plan.indexOf(id);
    return { prev: i > 0 ? plan[i - 1] : null, next: i >= 0 && i < plan.length - 1 ? plan[i + 1] : null };
  }
  function moduleHref(id) {
    return id === 'MODEL' && WB.views.model ? WB.href('model') : id === 'FIT' && WB.views.fit ? WB.href('fit') : WB.href('module/' + id);
  }
  function neighbourLink(id, dir) {
    if (!id) return null;
    const label = WB.moduleName(id);
    return el('a', { class: 'btn-s nb', href: moduleHref(id), rel: dir }, dir === 'prev' ? [WB.icon('arrow-left', { size: 12, stroke: 1.8 }), label] : [label, WB.icon('arrow-right', { size: 12, stroke: 1.8 })]);
  }
  WB.moduleView = function (canvas, run, id) {
    const root = el('div', { class: 'view view-module' });
    canvas.appendChild(root);
    const st = WB.stepStatus(id);
    const h = WB.handoff(id);
    const nb = stepNeighbours(id);
    const name = WB.moduleName(id);
    const top = el('div', { class: 'm-top' }, [
      el('div', { class: 'm-title' }, [WB.issuerNode({ sep: true }), el('h1', null, name), el('span', { class: 'm-code num' }, id), WB.statusChip(st)]),
      el('span', { class: 'p-sp' }),
      neighbourLink(nb.prev, 'prev'),
      neighbourLink(nb.next, 'next'),
      WB.collapseTool(() => root),
    ]);
    root.appendChild(el('div', { class: 'm-bar' }, top));
    const outline = [];
    const add = (anchor, label, na) => outline.push({ id: 'p-' + WB.cssId(anchor), label, na });
    const reason = WB.stepReason(id);
    if (!h) {
      root.appendChild(WB.panel({ title: 'Status', anchor: 'status', collapsible: false, body: el('div', { class: 'pad' }, [WB.statusChip(st), ' ', el('span', { class: 'm-reason' }, WB.inline(reason, id))]) }));
      root.appendChild(WB.conditionLine(name + ' did not run in this Pathway' + (reason ? ': ' + reason : '.')));
      add('status', 'Status');
      WB.setOutline(outline);
      WB.page.gapModules = [];
      return;
    }
    const q = WB.moduleQuestion(id);
    // the chip already says Blocked: a reason that starts "Blocked:" drops the repeated word
    const reasonText = String(reason || '').replace(/^Blocked:?\s*/i, '');
    const statusBody = el('div', { class: 'pad' }, [WB.statusChip(st), ' ', el('span', { class: 'm-reason' }, WB.inline(reasonText ? reasonText.charAt(0).toUpperCase() + reasonText.slice(1) : st === 'pass' ? 'No limitations recorded for this module.' : '', id))]);
    const qs = el('div', { class: 'm-qs' }, [
      q ? WB.panel({ title: 'Question', anchor: 'question', collapsible: false, className: 'panel-q', body: el('p', { class: 'm-q' }, q) }) : null,
      WB.panel({ title: 'Status', anchor: 'status', collapsible: false, body: statusBody }),
    ]);
    root.appendChild(qs);
    add('question', 'Question and status');
    // headline
    const paras = WB.paragraphs(h.analysis_md);
    if (paras.length) {
      const head = paras[0];
      const ids = [];
      head.replace(new RegExp(WB.CITE_TOKEN_SRC, 'g'), (m0, g) => g.split(',').forEach((x) => !ids.includes(x.trim()) && ids.push(x.trim())));
      const det = ids.length
        ? el('details', { class: 'srcs' }, [
            el('summary', null, [WB.icon('doc-stack', { size: 14 }), 'Sources (' + ids.length + ')']),
            el('ul', null, ids.map((cid) => {
              const c = WB.citation(id, cid);
              return el('li', null, [WB.citeChip(id, cid), el('span', { class: 'src-f' }, c ? c.source + ' · ' + c.locator : 'not found')]);
            })),
          ])
        : null;
      root.appendChild(
        WB.panel({
          title: 'Headline finding',
          anchor: 'headline',
          pinned: true,
          tags: [{ kind: 'model', label: 'Model-written' }],
          body: el('div', { class: 'pad headline' }, [el('p', { class: 'hl-p' }, WB.inline(head, id)), det]),
        })
      );
      add('headline', 'Headline finding');
    }
    // charts, then tables
    let n = 0;
    const code = id;
    WB.chartsForModule(id).forEach((c) => {
      n++;
      // the panel names the chart, so its caption is for assistive technology; the source line under the chart states where it comes from
      root.appendChild(WB.panel({ title: WB.chartTitle(c.chart_id), fig: WB.figNumber(code, n), anchor: 'c-' + c.chart_id, body: WB.chartSlot(c, { caption: false }), className: 'panel-chart' }));
      outline.push({ id: 'p-' + WB.cssId('c-' + c.chart_id), label: WB.chartTitle(c.chart_id) });
    });
    for (const tid of Object.keys(h.tables || {})) {
      const t = WB.table(tid);
      n++;
      // a table whose every value is n/a (a Blocked module) starts collapsed with that said in its head, not as a wall of n/a
      const allNa = t.rows.length > 0 && t.rows.every((row) => row.every((v, i) => t.columns[i] === 'cite' || WB.isEmpty(v)));
      const p = WB.tablePanel(t, { fig: WB.figNumber(code, n), link: false, anchor: tid, maxRows: 40, code: null, state: false, collapsed: allNa, note: allNa ? 'Every value is n/a' + (st === 'blocked' ? ': the module is Blocked' : '') : undefined });
      root.appendChild(p);
      outline.push({ id: p.id, label: WB.tableTitle(tid) });
    }
    // analysis
    if (paras.length > 1) {
      root.appendChild(
        WB.panel({
          title: 'Analysis',
          anchor: 'analysis',
          tags: [{ kind: 'model', label: 'Model-written' }],
          body: el('div', { class: 'pad md' }, WB.md(paras.slice(1).join('\n\n'), { module: id })),
        })
      );
      add('analysis', 'Analysis');
    }
    // gaps and limitations
    const gaps = WB.gapItems(id);
    const lims = ((run.limitations && run.limitations.cp5) || []).filter((l) => l.module_id === id);
    const body = el('div', { class: 'pad' });
    if (!gaps.length && !lims.length) body.appendChild(el('p', { class: 'muted' }, 'No gaps or limitations recorded for this module.'));
    if (gaps.length) {
      body.appendChild(
        el('ul', { class: 'gap-list' }, gaps.map((g) =>
          el('li', null, [
            el('span', { class: 'gl-ids' }, g.ids.length ? g.ids.map((gid) => WB.gapChip([gid], { label: gid, items: [g] })) : WB.gapChip([], { items: [g], label: 'gap', desc: { t: 'gap', ids: [], items: [g] } })),
            el('span', { class: 'gl-t' }, [el('strong', null, g.missing + '. '), WB.inline(g.text.slice(g.missing.length).replace(/^[\s:.]+/, ''), id)]),
          ])
        ))
      );
    }
    if (lims.length) {
      body.appendChild(el('h3', { class: 'sub-h' }, 'Evidence-check limitation'));
      lims.forEach((l) => body.appendChild(el('dl', { class: 'lim' }, [el('dt', null, 'Limitation'), el('dd', null, WB.inline(l.limitation, id)), el('dt', null, 'Effect on the decision'), el('dd', null, l.effect_on_decision), el('dt', null, 'Source that would lift it'), el('dd', null, l.source_that_would_lift)])));
    }
    root.appendChild(WB.panel({ title: 'Gaps and limitations', anchor: 'gaps', pinned: true, body }));
    add('gaps', 'Gaps and limitations');
    const foot = el('nav', { class: 'm-foot', 'aria-label': 'Previous and next module' }, [neighbourLink(nb.prev, 'prev'), el('span', { class: 'p-sp' }), neighbourLink(nb.next, 'next')]);
    root.appendChild(foot);
    WB.setOutline(outline);
    WB.page.gapModules = [id];
  };
  WB.registerView('module', {
    title: 'Analysis',
    icon: 'analysis',
    available: (run) => ((run.plan || []).length ? true : 'This run has no plan.'),
    render(canvas, run, params) {
      const id = params.id || (run.plan || [])[0];
      if (!id || !(run.plan || []).includes(id)) {
        const root = el('div', { class: 'view' });
        root.appendChild(el('div', { class: 'm-bar' }, el('div', { class: 'm-title' }, el('h1', null, 'Module not found'))));
        root.appendChild(WB.conditionLine('This run has no module "' + (id || '') + '". Modules in this run: ' + (run.plan || []).join(', ') + '.'));
        canvas.appendChild(root);
        WB.setOutline([]);
        return;
      }
      WB.moduleView(canvas, run, id);
    },
  });

  /* ---------- Evidence ---------- */
  function docIcon(src) {
    const s = String(src);
    if (/TEST DATA/i.test(s)) return 'flask';
    if (/earnings|release/i.test(s)) return 'doc-earnings';
    if (/agreement|indenture|merger|clause|legal|credit_agreement/i.test(s)) return 'doc-legal';
    if (/trace|market|levels|price|quote/i.test(s)) return 'doc-market';
    if (/portfolio|mandate|exposure|limits|positions/i.test(s)) return 'doc-portfolio';
    if (/^https?:|fetched|web/i.test(s)) return 'doc-web';
    return 'doc-filing';
  }
  WB.docIcon = docIcon;
  function placeLink(place) {
    if (place.kind === 'analysis') return { href: WB.href('module/' + place.module + '/p-analysis'), label: WB.moduleName(place.module) + ', analysis' };
    if (place.kind === 'table') {
      const owner = place.module === 'RUN_BRIEF' ? null : place.module;
      return { href: owner ? WB.href('module/' + owner + '/t-' + WB.cssId(place.table)) : WB.href('front'), label: WB.tableTitle(place.table) + ' row ' + (place.row + 1) };
    }
    return { href: WB.views.model ? WB.href('model') : WB.href('module/MODEL'), label: 'Model, ' + place.line };
  }
  WB.registerView('evidence', {
    title: 'Evidence',
    icon: 'evidence',
    available: () => true,
    render(canvas, run, params) {
      const root = el('div', { class: 'view view-evidence' });
      canvas.appendChild(root);
      const all = [];
      for (const [hid, h] of Object.entries(run.handoffs || {})) for (const c of h.citations || []) all.push(Object.assign({ module: hid }, c));
      const sources = Array.from(new Set(all.map((c) => c.source))).sort();
      const modules = Array.from(new Set(all.map((c) => c.module)));
      const real = all.filter((c) => !c.synthetic).length;
      const state = { kind: 'all', source: '', module: '', q: '', limit: 60 };
      root.appendChild(el('div', { class: 'm-bar' }, el('div', { class: 'm-title' }, [WB.issuerNode({ sep: true }), el('h1', null, 'Evidence'), el('span', { class: 'm-code num' }, all.length + ' citations'), el('span', { class: 'm-sub' }, real + ' real, ' + (all.length - real) + ' synthetic'), el('span', { class: 'p-sp' })])));
      const list = el('div', { class: 'ev-list', role: 'list' });
      const count = el('span', { class: 'ev-count', 'aria-live': 'polite' });
      const more = el('button', { type: 'button', class: 'btn-s more' }, 'Show more');
      const chip = (label, kind, n) => {
        const b = el('button', { type: 'button', class: 'fchip' + (state.kind === kind ? ' on' : ''), 'aria-pressed': state.kind === kind ? 'true' : 'false' }, [label, ' ', el('span', { class: 'num' }, String(n))]);
        b.addEventListener('click', () => {
          state.kind = kind;
          state.limit = 60;
          paintChips();
          paint();
        });
        return b;
      };
      const chips = el('div', { class: 'ev-chips', role: 'group', 'aria-label': 'Filter by kind' });
      function paintChips() {
        chips.replaceChildren(chip('All', 'all', all.length), chip('Real', 'real', real), chip('Synthetic', 'synthetic', all.length - real));
      }
      paintChips();
      const sel = (label, opts, key) => {
        const s = el('select', { 'aria-label': label, class: 'sel' }, [el('option', { value: '' }, label)].concat(opts.map((o) => el('option', { value: o.v }, o.l))));
        s.addEventListener('change', () => {
          state[key] = s.value;
          state.limit = 60;
          paint();
        });
        return s;
      };
      const input = el('input', { type: 'search', class: 'txt-in', placeholder: 'Search excerpts and files', 'aria-label': 'Search citations' });
      input.addEventListener('input', () => {
        state.q = input.value.trim().toLowerCase();
        state.limit = 60;
        paint();
      });
      root.appendChild(
        el('div', { class: 'ev-tools' }, [chips, sel('All source files', sources.map((s) => ({ v: s, l: s })), 'source'), sel('All modules', modules.map((m) => ({ v: m, l: WB.moduleName(m) + ' (' + m + ')' })), 'module'), input, count])
      );
      root.appendChild(list);
      root.appendChild(el('div', { class: 'ev-more' }, more));
      const matches = () =>
        all.filter((c) => (state.kind === 'all' || (state.kind === 'real') === !c.synthetic) && (!state.source || c.source === state.source) && (!state.module || c.module === state.module) && (!state.q || (c.source + ' ' + c.locator + ' ' + c.excerpt + ' ' + c.id).toLowerCase().includes(state.q)));
      let target = null;
      if (params.anchor && /^ev-/.test(params.anchor)) target = params.anchor;
      function row(c) {
        const uses = WB.citationUses(c.module, c.id);
        const places = uses.slice(0, 3).map((p) => {
          const l = placeLink(p);
          return el('a', { href: l.href, class: 'place' }, l.label);
        });
        return el('article', { class: 'ev-row', role: 'listitem', id: 'ev-' + WB.cssId(c.module + '-' + c.id) }, [
          el('div', { class: 'ev-id' }, [WB.citeChip(c.module, c.id), el('span', { class: 'ev-mod num' }, c.module)]),
          el('div', { class: 'ev-src' }, [WB.icon(docIcon(c.source), { size: 14 }), el('span', { class: 'ev-file' }, c.source), el('span', { class: 'ev-loc num' }, c.locator)]),
          el('p', { class: 'ev-ex' }, c.excerpt),
          el('div', { class: 'ev-used' }, [el('span', { class: 'num' }, uses.length + (uses.length === 1 ? ' place' : ' places')), places]),
        ]);
      }
      function paint() {
        const m = matches();
        if (target) {
          const i = m.findIndex((c) => 'ev-' + WB.cssId(c.module + '-' + c.id) === target);
          if (i >= state.limit) state.limit = i + 20;
        }
        list.replaceChildren(...m.slice(0, state.limit).map(row));
        count.textContent = Math.min(state.limit, m.length) + ' of ' + m.length + ' shown';
        more.hidden = m.length <= state.limit;
        if (!m.length) list.appendChild(WB.conditionLine('No citation matches these filters.'));
      }
      more.addEventListener('click', () => {
        state.limit += 60;
        paint();
      });
      paint();
      WB.setOutline([{ id: 'ev-top', label: 'Citations' }]);
      root.id = 'ev-top';
      WB.page.gapModules = [];
    },
  });

  /* ---------- Limitations ---------- */
  WB.registerView('limitations', {
    title: 'Limitations',
    icon: 'limitations',
    available: () => true,
    render(canvas, run) {
      const root = el('div', { class: 'view view-lim' });
      canvas.appendChild(root);
      root.appendChild(el('div', { class: 'm-bar' }, el('div', { class: 'm-title' }, [WB.issuerNode({ sep: true }), el('h1', null, 'Limitations'), el('span', { class: 'p-sp' }), WB.collapseTool(() => root)])));
      const L = run.limitations || {};
      const outline = [];
      const sect = (anchor, title, body, note) => {
        const p = WB.panel({ title, anchor, note, body: el('div', { class: 'pad' }, body) });
        root.appendChild(p);
        outline.push({ id: p.id, label: title });
      };
      const limItem = (o) => {
        if (typeof o === 'string') return el('li', { class: 'lim-i' }, WB.inline(o));
        if (o && o.limitation) {
          return el('li', { class: 'lim-i' }, [
            el('div', { class: 'lim-h' }, [el('a', { href: moduleHref(o.module_id), class: 'num' }, o.module_id), el('strong', null, WB.moduleName(o.module_id))]),
            el('dl', { class: 'lim' }, [el('dt', null, 'Limitation'), el('dd', null, WB.inline(o.limitation, o.module_id)), el('dt', null, 'Effect on the decision'), el('dd', null, o.effect_on_decision), el('dt', null, 'Source that would lift it'), el('dd', null, o.source_that_would_lift)]),
          ]);
        }
        return el('li', { class: 'lim-i' }, el('code', null, JSON.stringify(o)));
      };
      sect('approval', 'Shown at Approval', (L.approval || []).length ? el('ul', { class: 'lim-l' }, L.approval.map(limItem)) : WB.conditionLine('None recorded at Approval for this run.'));
      sect('cp5', 'Found by the evidence check', (L.cp5 || []).length ? el('ul', { class: 'lim-l' }, L.cp5.map(limItem)) : WB.conditionLine('The evidence check recorded none.'), (L.cp5 || []).length + ' modules');
      sect('unforeseen', 'Unforeseen', (L.unforeseen || []).length ? el('ul', { class: 'lim-l' }, L.unforeseen.map(limItem)) : WB.conditionLine('None found during the run.'));
      const steps = run.steps || {};
      const notRun = Object.keys(steps).filter((k) => steps[k].status === 'skipped');
      const blocked = Object.keys(steps).filter((k) => WB.stepStatus(k) === 'blocked');
      sect(
        'notrun',
        'Steps not run and blocked modules',
        [
          notRun.length ? notRun.map((k) => WB.conditionLine(WB.moduleName(k) + ' (' + k + '): not run, ' + (steps[k].reason || 'no reason recorded') + '.')) : WB.conditionLine('Every planned step ran.'),
          blocked.map((k) => el('div', { class: 'blk' }, [WB.statusChip('blocked'), ' ', el('a', { href: moduleHref(k) }, WB.moduleName(k)), el('span', { class: 'num muted' }, ' ' + k), ' ', el('span', null, WB.inline(WB.stepReason(k), k))])),
        ]
      );
      WB.setOutline(outline);
      WB.page.gapModules = [];
    },
  });
  WB.moduleHref = moduleHref;
})();
