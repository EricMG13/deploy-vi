/* WB charts: WB.chart(host, chartRecord, opts) draws every chart record of an rbot-run/1 as inline SVG.
   One engine per mark family (columns, waterfall, bullets, dumbbells, range strips, lines, scatter, matrix, tornado, debt stack);
   one builder per chart_id maps the twin tables to marks (interfaces §11.4). Every mark is a focusable g (hit area >= 24px) with an
   accessible name, a tooltip and a passport descriptor on the twin table's cell. No innerHTML, no canvas, no library. */
(function () {
  'use strict';
  const WB = window.WB;
  const el = WB.el;
  const S = WB.svg;
  let UID = 0;
  const NA_GAP = '—';

  /* ---------- numbers and text ---------- */
  function num(v, lenient) {
    const t = String(v == null ? '' : v).trim();
    if (!t || WB.isEmpty(t)) return NaN;
    if (WB.isNumeric(t)) {
      const neg = /^\(.*\)/.test(t) || /^[-−]/.test(t);
      const m = /\d[\d,]*\.?\d*|\.\d+/.exec(t);
      const n = parseFloat(m[0].replace(/,/g, ''));
      return neg ? -n : n;
    }
    if (lenient) {
      let m = /\((\d+(?:\.\d+)?)\)\s*$/.exec(t);
      if (m) return parseFloat(m[1]);
      m = /^([-−]?\d[\d,]*\.?\d*)\s*[A-Za-z%]+/.exec(t);
      if (m) return parseFloat(m[1].replace(/,/g, '').replace('−', '-'));
    }
    return NaN;
  }
  const decimals = (v) => {
    const m = /\.(\d+)/.exec(String(v));
    return m ? m[1].length : 0;
  };
  function fmtComputed(n, d) {
    const a = Math.abs(n).toFixed(d).split('.');
    a[0] = a[0].replace(/\B(?=(\d{3})+(?!\d))/g, ',');
    const s = a.join('.');
    return n < 0 ? '(' + s + ')' : s;
  }
  /* exact sum of decimal strings: scaled integers, printed with the inputs' decimals */
  function sumExact(raws) {
    let d = 0;
    raws.forEach((v) => (d = Math.max(d, decimals(v))));
    const f = Math.pow(10, d);
    let t = 0;
    raws.forEach((v) => (t += Math.round(num(v) * f)));
    return { n: t / f, text: fmtComputed(t / f, d) };
  }
  const tw = (t, px, mono) => String(t).length * px * (mono ? 0.62 : 0.54);
  function wrapText(text, maxW, px) {
    const words = String(text).split(/\s+/);
    const lines = [];
    let cur = '';
    for (const w of words) {
      const next = cur ? cur + ' ' + w : w;
      if (tw(next, px) <= maxW || !cur) cur = next;
      else {
        lines.push(cur);
        cur = w;
      }
    }
    if (cur) lines.push(cur);
    return lines;
  }
  function niceScale(lo, hi, n, zero, integer) {
    if (zero !== false) {
      lo = Math.min(lo, 0);
      hi = Math.max(hi, 0);
    }
    if (!isFinite(lo) || !isFinite(hi)) {
      lo = 0;
      hi = 1;
    }
    if (lo === hi) hi = lo + 1;
    const raw = (hi - lo) / Math.max(1, n);
    const p = Math.pow(10, Math.floor(Math.log10(raw)));
    const r = raw / p;
    let step = (r <= 1 ? 1 : r <= 2 ? 2 : r <= 2.5 ? 2.5 : r <= 5 ? 5 : 10) * p;
    if (integer) step = Math.max(1, Math.ceil(step));
    const a = Math.floor(lo / step + 1e-9) * step;
    const b = Math.ceil(hi / step - 1e-9) * step;
    const ticks = [];
    for (let t = a; t <= b + step / 2; t += step) ticks.push(+t.toFixed(10));
    return { lo: a, hi: b, ticks, step };
  }
  function fmtTick(t, step) {
    const d = step < 1 ? Math.min(3, (String(+step.toFixed(6)).split('.')[1] || '').length) : 0;
    const s = Math.abs(t).toLocaleString('en-US', { minimumFractionDigits: d, maximumFractionDigits: d });
    return t < 0 ? '−' + s : s;
  }
  const lin = (d0, d1, r0, r1) => (v) => r0 + ((v - d0) / (d1 - d0 || 1)) * (r1 - r0);
  const lab = (raw) => {
    const t = String(raw).trim();
    const m = /^([-\u2212]?)(\d{4,})(\.\d+)?$/.exec(t);
    if (!m) return WB.fmtNum(t);
    const body = m[2].replace(/\B(?=(\d{3})+(?!\d))/g, ',') + (m[3] || '');
    return m[1] ? '(' + body + ')' : body;
  };
  const pad = (lo, hi, f) => {
    const d = (hi - lo) || Math.abs(hi) || 1;
    return [lo - d * f, hi + d * f];
  };
  const unitText = (u) => {
    const s = String(u || '');
    if (/^USD m(illions)?$/i.test(s) || /^MILLIONS$/.test(s)) return 'US$ m';
    return s.replace(/^USD millions/, 'US$ m');
  };
  const gridLayout = (W, n, minW, gap) => {
    const g = gap == null ? 18 : gap;
    const cols = Math.max(1, Math.min(n, Math.floor((W + g) / (minW + g))));
    return { cols, pw: (W - g * (cols - 1)) / cols, gap: g };
  };

  /* ---------- context: one per draw ---------- */
  function twinOf(ctx, tid) {
    const t = ctx.twins.find((x) => x.twinOf === tid);
    if (!t) throw new Error('chart ' + ctx.chart.chart_id + ': table ' + tid + ' is not in its data');
    return t;
  }
  const optTwin = (ctx, tid) => ctx.twins.find((x) => x.twinOf === tid) || null;
  function colIdx(t, name) {
    const i = t.columns.indexOf(name);
    if (i < 0) throw new Error('chart column missing: ' + t.id + '.' + name);
    return i;
  }
  /* provenance of one twin cell: k = solid | syn | soft | gap */
  function og(ctx, t, r, col) {
    const c = colIdx(t, col);
    let kind = WB.cellOrigin(t, r, c).kind;
    if (kind === 'plain' || kind === 'none') kind = ctx.chart.origin === 'model' ? 'model' : 'plain';
    const k = kind === 'gap' ? 'gap' : kind === 'synthetic' ? 'syn' : kind === 'model' || kind === 'illustrative' ? 'soft' : 'solid';
    return { k, kind, word: kind === 'plain' ? '' : (WB.originWord[kind] || '').toLowerCase() };
  }
  /* a numeric datum read from a twin cell */
  function item(ctx, t, r, col, base) {
    const c = colIdx(t, col);
    const raw = t.rows[r][c];
    const v = num(raw, base && base.lenient);
    const o = og(ctx, t, r, col);
    return Object.assign({ v, raw, desc: { t: 'cell', table: t.id, r, c }, k: isNaN(v) ? 'gap' : o.k === 'gap' ? 'gap' : o.k, word: o.word, t, r, col }, base);
  }
  function aggDesc(t, rows, title, sub, what, text) {
    const cites = [];
    const seen = new Set();
    rows.forEach((r) => {
      const info = WB.rowInfo(t, r);
      if (!info) return;
      info.citations.forEach((c) => {
        const key = c.module + ':' + c.id;
        if (seen.has(key)) return;
        seen.add(key);
        cites.push({ id: c.id, module: c.module, label: (c.source || '') + (c.locator ? ' · ' + c.locator : ''), synthetic: !!c.synthetic, missing: !!c.missing, desc: { t: 'cite', module: c.module, id: c.id } });
      });
    });
    return { t: 'note', kind: 'calculated', code: t.twinOf || t.id, title, sub, fields: [[what, text, true], ['Rows', rows.length + ' in the chart table', false]], note: 'Added up from the chart table rows. The Table tab lists each row; the sources below are the rows’ own.', cites, table: { id: t.id, row: rows[0], col: -1 } };
  }
  function worst(items) {
    const k = items.some((i) => i.k === 'soft') ? 'soft' : items.some((i) => i.k === 'syn') ? 'syn' : 'solid';
    const words = Array.from(new Set(items.map((i) => i.word).filter(Boolean)));
    return { k, word: words.join(' / ') };
  }
  function paintAttrs(ctx, cls, k) {
    if (k === 'soft') {
      ctx.seen.soft = true;
      return { class: 'sh ' + cls + ' o-soft', style: 'fill:' + hatch(ctx, cls) };
    }
    if (k === 'syn') {
      ctx.seen.syn = true;
      return { class: 'sh ' + cls + ' o-syn' };
    }
    ctx.seen.solid = true;
    return { class: 'sh ' + cls };
  }
  function hatchIn(defs, id, cls) {
    defs.appendChild(S('pattern', { id, class: cls, width: 5, height: 5, patternUnits: 'userSpaceOnUse', patternTransform: 'rotate(45)' }, [S('rect', { width: 5, height: 5, class: 'hp-bg' }), S('line', { x1: 0, y1: 0, x2: 0, y2: 5, class: 'hp-ln' })]));
  }
  function hatch(ctx, cls) {
    const key = cls.split(' ')[0];
    if (!ctx.patterns[key]) {
      const id = 'wbh' + ctx.uid + '-' + key;
      hatchIn(ctx.defs, id, key);
      ctx.patterns[key] = id;
    }
    return 'url(#' + ctx.patterns[key] + ')';
  }
  const shape = (ctx, tag, attrs, cls, k) => S(tag, Object.assign({}, attrs, paintAttrs(ctx, cls, k)));
  const nm = (...p) => p.filter((x) => x !== '' && x != null && x !== false).join(', ');
  /* a value with its unit in the house style: 3.48x, 12%, US$12m; other units follow after a space */
  const withUnitTight = (v, unit) => {
    if (!v) return '';
    const u = String(unit || '');
    if (u === 'x' || u === '%') return v + u;
    if (/^US\$ ?m$/.test(u)) return /^\(/.test(v) ? '(US$' + v.slice(1, -1) + 'm)' : 'US$' + v + 'm';
    return u ? v + ' ' + u : v;
  };
  const withUnit = (raw, unit) => lab(raw) + (unit ? ' ' + unit : '');
  function itemName(it, series, cat, unit) {
    if (it.k === 'gap') return gapName(it, series, cat);
    return nm(series, cat) + ': ' + withUnit(it.raw, unit) + (it.word ? ', ' + it.word : '') + (it.extra ? ', ' + it.extra : '');
  }
  function gapIds(it) {
    const g = WB.cellGap(it.t, it.r, colIdx(it.t, it.col));
    return (g && g.item && g.item.ids) || [];
  }
  function gapName(it, series, cat) {
    const ids = gapIds(it);
    const raw = String(it.raw == null ? '' : it.raw);
    return nm(series, cat) + ': n/a' + (ids.length ? ', gap ' + ids.join(' ') : '') + (raw && !WB.isEmpty(raw) ? ', served as ' + raw : '');
  }

  /* ---------- marks ---------- */
  function mark(ctx, o) {
    const w = Math.max(24, o.w);
    const h = Math.max(24, o.h);
    const g = S('g', { class: 'mk' + (o.cls ? ' ' + o.cls : ''), tabindex: -1, role: 'button', 'aria-label': o.label, 'data-ref': WB.ref(o.desc) });
    g.appendChild(S('rect', { class: 'hit', x: o.x + o.w / 2 - w / 2, y: o.y + o.h / 2 - h / 2, width: w, height: h }));
    (o.kids || []).forEach((k) => k && g.appendChild(k));
    g._tip = o.label;
    ctx.marks.push(g);
    ctx.svg.appendChild(g);
    return g;
  }
  function gapMark(ctx, x, y, it, series, cat) {
    ctx.seen.gap = true;
    const ids = gapIds(it);
    const kids = [S('text', { class: 'na', x, y, 'text-anchor': 'middle', text: 'n/a' })];
    if (ids.length) kids.push(S('text', { class: 'na-id', x, y: y + 10, 'text-anchor': 'middle', text: ids.join(' ') }));
    return mark(ctx, { x: x - 14, y: y - 11, w: 28, h: ids.length ? 24 : 14, label: gapName(it, series, cat), desc: it.desc, kids, cls: 'mk-gap' });
  }
  function icon(name, x, y, size, cls) {
    const i = WB.icon(name, { size });
    i.setAttribute('x', x);
    i.setAttribute('y', y);
    i.setAttribute('class', (i.getAttribute('class') || '') + ' ' + cls);
    return i;
  }
  const T = (x, y, text, cls, anchor) => S('text', { x, y, class: cls, 'text-anchor': anchor || 'start', text });

  /* ---------- axes ---------- */
  function axisV(ctx, sc, y, x0, x1) {
    const g = S('g', { class: 'grid', 'aria-hidden': 'true' });
    sc.ticks.forEach((t) => {
      const yy = Math.round(y(t)) + 0.5;
      g.appendChild(S('line', { x1: x0, x2: x1, y1: yy, y2: yy, class: t === 0 ? 'zero' : '' }));
      g.appendChild(T(x0 - 6, yy + 3.5, fmtTick(t, sc.step), 'ax', 'end'));
    });
    ctx.svg.appendChild(g);
  }
  function axisH(ctx, sc, x, y0, y1, fmt) {
    const g = S('g', { class: 'grid', 'aria-hidden': 'true' });
    sc.ticks.forEach((t) => {
      const xx = Math.round(x(t)) + 0.5;
      g.appendChild(S('line', { x1: xx, x2: xx, y1: y0, y2: y1, class: t === 0 ? 'zero' : '' }));
      g.appendChild(T(xx, y1 + 13, fmt ? fmt(t) : fmtTick(t, sc.step), 'ax', 'middle'));
    });
    ctx.svg.appendChild(g);
  }
  function catLabel(ctx, x, y, text, maxW, anchor, lh) {
    const lines = wrapText(text, maxW, 11);
    const t = S('text', { class: 'cat', x, y, 'text-anchor': anchor || 'middle' });
    lines.forEach((ln, i) => t.appendChild(S('tspan', { x, dy: i === 0 ? 0 : lh || 12.5, text: ln })));
    ctx.svg.appendChild(t);
    return lines.length;
  }

  /* ---------- engine: columns (vertical or horizontal; grouped or stacked; optional panels) ---------- */
  function engineColumns(ctx, sp) {
    const W = ctx.W;
    const horiz = sp.orient === 'h';
    const stack = sp.mode === 'stack';
    const nS = sp.series.length;
    let lo = 0;
    let hi = 0;
    sp.panels.forEach((p) =>
      p.cats.forEach((c) => {
        if (stack) {
          let pos = 0;
          let neg = 0;
          c.items.forEach((i) => !isNaN(i.v) && (i.v >= 0 ? (pos += i.v) : (neg += i.v)));
          hi = Math.max(hi, pos);
          lo = Math.min(lo, neg);
        } else c.items.forEach((i) => !isNaN(i.v) && ((hi = Math.max(hi, i.v)), (lo = Math.min(lo, i.v))));
        if (c.rule && !isNaN(c.rule.v)) hi = Math.max(hi, c.rule.v);
      })
    );
    if (sp.max != null) hi = Math.max(hi, sp.max);
    const sc = niceScale(lo, hi, horiz ? 5 : 4, true, sp.integer);
    const valueLabel = (i) => i.txt || lab(i.raw);
    if (horiz) return columnsH(ctx, sp, sc, stack, nS, valueLabel);
    const grid = gridLayout(W, sp.panels.length, sp.minPanelW || 300);
    const plotH = ctx.opts.compact ? 120 : sp.plotH || 160;
    const maxCats = Math.max.apply(null, sp.panels.map((p) => p.cats.length));
    const bandMin = (grid.pw - 50) / maxCats;
    let maxLines = 1;
    sp.panels.forEach((p) => p.cats.forEach((c) => (maxLines = Math.max(maxLines, wrapText(c.label, Math.max(40, (grid.pw - 50) / p.cats.length - 6), 11).length))));
    const hasSub = sp.panels.some((p) => p.cats.some((c) => c.sub));
    const titleH = sp.panels.some((p) => p.title) ? 20 : 0;
    const panelH = titleH + 14 + plotH + 8 + maxLines * 12.5 + (hasSub ? 12.5 : 0) + 8;
    const rows = Math.ceil(sp.panels.length / grid.cols);
    sp.panels.forEach((p, pi) => {
      const ox = (pi % grid.cols) * (grid.pw + grid.gap);
      const oy = Math.floor(pi / grid.cols) * panelH;
      const L = ox + 46;
      const R = ox + grid.pw - 6;
      const top = oy + titleH + 14;
      const bot = top + plotH;
      const y = lin(sc.lo, sc.hi, bot, top);
      if (p.title) ctx.svg.appendChild(T(ox + 2, oy + 12, p.title, 'ttl'));
      axisV(ctx, sc, y, L, R);
      const band = (R - L) / p.cats.length;
      p.cats.forEach((c, ci) => {
        const cx = L + band * (ci + 0.5);
        catLabel(ctx, cx, bot + 14, c.label, Math.max(40, band - 6), 'middle');
        // a second line under every category (e.g. the recovery %), at one height across the panel
        if (c.sub) ctx.svg.appendChild(T(cx, bot + 14 + maxLines * 12.5, c.sub, 'cat sub', 'middle'));
        const bw = stack ? Math.min(54, band - 14) : Math.max(8, Math.min(36, Math.floor((band - 12) / nS)));
        let pos = 0;
        let neg = 0;
        let allGap = true;
        c.items.forEach((it, ii) => {
          const ser = sp.series[it.s];
          if (isNaN(it.v)) {
            const gx = stack ? cx : cx - (bw * nS) / 2 + bw * ii + bw / 2;
            gapMark(ctx, gx, bot - 6 - (stack ? ii * 22 : 0), it, ser.label, c.label);
            return;
          }
          allGap = false;
          let v0 = 0;
          let v1 = it.v;
          let x = cx - bw / 2;
          if (stack) {
            v0 = it.v >= 0 ? pos : neg;
            v1 = v0 + it.v;
            if (it.v >= 0) pos = v1;
            else neg = v1;
          } else x = cx - (bw * nS) / 2 + bw * ii;
          const yt = Math.min(y(v0), y(v1));
          const hh = Math.max(Math.abs(y(v1) - y(v0)), 1.5);
          const rect = shape(ctx, 'rect', { x, y: yt, width: bw - (stack ? 0 : 2), height: hh }, ser.cls, it.k);
          const kids = [rect];
          if (!stack) {
            const txt = valueLabel(it);
            if (bw >= tw(txt, 10.5, true) - 4) kids.push(T(x + (bw - 2) / 2, it.v >= 0 ? yt - 3 : yt + hh + 10, txt, 'val', 'middle'));
          }
          mark(ctx, { x, y: yt, w: bw, h: hh, label: itemName(it, ser.label, c.label, sp.unit), desc: it.desc, kids });
        });
        if (stack && c.total && !allGap) ctx.svg.appendChild(T(cx, y(pos) - 4, c.total, 'val tot', 'middle'));
        if (c.rule) {
          const r = c.rule;
          if (isNaN(r.v)) gapMark(ctx, cx, bot - 6, r, r.label, c.label);
          else {
            const yy = y(r.v);
            const rw = Math.min(band - 4, 64);
            const overBar = stack && !allGap && yy > y(pos) + 4;
            mark(ctx, { x: cx - rw / 2, y: yy - 1, w: rw, h: 2, label: itemName(r, r.label, c.label, sp.unit), desc: r.desc, kids: [S('line', { x1: cx - rw / 2, x2: cx + rw / 2, y1: yy, y2: yy, class: 'rule-mk' }), overBar ? null : T(cx, yy - 5, lab(r.raw), 'val', 'middle')] });
          }
        }
      });
    });
    return rows * panelH;
  }
  function columnsH(ctx, sp, sc, stack, nS, valueLabel) {
    const W = ctx.W;
    const p = sp.panels[0];
    const maxLab = Math.max.apply(null, p.cats.map((c) => tw(c.label, 11)));
    const LW = Math.max(90, Math.min(W * 0.4, maxLab + 12, 260));
    const L = LW;
    const R = W - 58;
    const bh = stack ? 14 : 12;
    const rowsH = p.cats.map((c) => Math.max(stack ? 24 : nS * (bh + 2) + 10, wrapText(c.label, LW - 10, 11).length * 12.5 + 8));
    const top = 6;
    const total = rowsH.reduce((a, b) => a + b, 0);
    const bot = top + total;
    const x = lin(sc.lo, sc.hi, L, R);
    axisH(ctx, sc, x, top, bot);
    let yy = top;
    p.cats.forEach((c, ci) => {
      const rh = rowsH[ci];
      const mid = yy + rh / 2;
      const lines = wrapText(c.label, LW - 10, 11);
      const t = S('text', { class: 'cat', x: LW - 8, y: mid - ((lines.length - 1) * 12.5) / 2 + 4, 'text-anchor': 'end' });
      lines.forEach((ln, i) => t.appendChild(S('tspan', { x: LW - 8, dy: i === 0 ? 0 : 12.5, text: ln })));
      ctx.svg.appendChild(t);
      let pos = 0;
      let neg = 0;
      c.items.forEach((it, ii) => {
        const ser = sp.series[it.s];
        const by = stack ? mid - bh / 2 : mid - (nS * (bh + 2)) / 2 + ii * (bh + 2);
        if (isNaN(it.v)) {
          gapMark(ctx, x(0) + 18 + (stack ? ii * 42 : 0), by + bh - 1, it, ser.label, c.label);
          return;
        }
        let v0 = 0;
        let v1 = it.v;
        if (stack) {
          v0 = it.v >= 0 ? pos : neg;
          v1 = v0 + it.v;
          if (it.v >= 0) pos = v1;
          else neg = v1;
        }
        const xl = Math.min(x(v0), x(v1));
        const ww = Math.max(Math.abs(x(v1) - x(v0)), 1.5);
        const kids = [shape(ctx, 'rect', { x: xl, y: by, width: ww, height: bh }, ser.cls, it.k)];
        if (!stack) kids.push(it.v >= 0 ? T(xl + ww + 4, by + bh - 2, valueLabel(it), 'val') : T(xl - 4, by + bh - 2, valueLabel(it), 'val', 'end'));
        mark(ctx, { x: xl, y: by, w: ww, h: bh, label: itemName(it, ser.label, c.label, sp.unit), desc: it.desc, kids });
      });
      if (stack && c.total) ctx.svg.appendChild(T(x(pos) + 4, mid + 4, c.total, 'val tot'));
      yy += rh;
    });
    if (sp.unit) ctx.svg.appendChild(T(R, bot + 28, sp.unit, 'ax unit', 'end'));
    return bot + 34;
  }

  /* ---------- engine: waterfall ---------- */
  function engineWaterfall(ctx, sp) {
    const W = ctx.W;
    const panels = sp.panels.map((p) => {
      let running = null;
      const steps = [];
      p.steps.forEach((s, i) => {
        if (s.kind === 'total') {
          if (running != null && Math.abs(running - s.v) > 0.0051) {
            const diff = s.v - running;
            steps.push({ kind: 'residual', label: 'Unexplained residual', v: diff, from: running, to: s.v, raw: fmtComputed(diff, Math.max(decimals(s.raw), 0)), residual: true, stated: s });
            ctx.notes.push((p.title ? p.title + ': the steps do not reconcile. ' : 'The steps do not reconcile. ') + 'They add up to ' + fmtComputed(running, decimals(s.raw)) + ' but the table states ' + lab(s.raw) + ' (' + (s.label || 'total') + '), a residual of ' + fmtComputed(diff, decimals(s.raw)) + ', drawn as the unexplained step.');
          }
          steps.push(Object.assign({}, s, { from: 0, to: s.v }));
          running = s.v;
        } else {
          const from = running == null ? 0 : running;
          steps.push(Object.assign({}, s, { from, to: from + s.v }));
          running = from + s.v;
        }
      });
      return { title: p.title, steps };
    });
    let lo = 0;
    let hi = 0;
    panels.forEach((p) => p.steps.forEach((s) => ((lo = Math.min(lo, s.from, s.to)), (hi = Math.max(hi, s.from, s.to)))));
    const sc = niceScale(lo, hi, 4);
    const grid = gridLayout(W, panels.length, sp.minPanelW || 420);
    // narrow bands (many steps, or a half-width slot): the bridge turns on its side, step names on the left as rows
    const maxSteps = Math.max.apply(null, panels.map((p) => p.steps.length));
    if ((grid.pw - 52) / maxSteps < 58) return waterfallH(ctx, sp, panels, sc);
    const plotH = ctx.opts.compact ? 130 : sp.plotH || 170;
    let maxLines = 1;
    panels.forEach((p) => p.steps.forEach((s) => (maxLines = Math.max(maxLines, wrapText(s.label, Math.max(36, (grid.pw - 50) / p.steps.length - 4), 11).length))));
    const titleH = panels.some((p) => p.title) ? 20 : 0;
    const panelH = titleH + 22 + plotH + 8 + maxLines * 12.5 + 10;
    panels.forEach((p, pi) => {
      const ox = (pi % grid.cols) * (grid.pw + grid.gap);
      const oy = Math.floor(pi / grid.cols) * panelH;
      const L = ox + 46;
      const R = ox + grid.pw - 6;
      const top = oy + titleH + 22;
      const bot = top + plotH;
      const y = lin(sc.lo, sc.hi, bot, top);
      if (p.title) ctx.svg.appendChild(T(ox + 2, oy + 12, p.title, 'ttl'));
      axisV(ctx, sc, y, L, R);
      const band = (R - L) / p.steps.length;
      const bw = Math.min(46, Math.max(10, band - 8));
      // connectors first so marks sit above them
      p.steps.forEach((s, i) => {
        if (i === p.steps.length - 1) return;
        const lvl = y(s.to);
        const cx = L + band * (i + 0.5);
        ctx.svg.appendChild(S('line', { class: 'conn', x1: cx + bw / 2, x2: cx + band - bw / 2 + 0, y1: lvl, y2: lvl, 'aria-hidden': 'true' }));
      });
      p.steps.forEach((s, i) => {
        const cx = L + band * (i + 0.5);
        catLabel(ctx, cx, bot + 14, s.label, Math.max(36, band - 4), 'middle');
        const yt = Math.min(y(s.from), y(s.to));
        const hh = Math.max(Math.abs(y(s.to) - y(s.from)), 1.5);
        const x = cx - bw / 2;
        let cls = s.cls || (s.kind === 'total' ? 'sr-2' : s.v >= 0 ? 'sr-0' : 'sr-1');
        const kids = [];
        if (s.residual) {
          ctx.seen.residual = true;
          kids.push(S('rect', { x, y: yt, width: bw, height: hh, class: 'sh sg-neg res' }));
        } else kids.push(shape(ctx, 'rect', { x, y: yt, width: bw, height: hh, class: s.dashed ? 'dashed' : '' }, cls, s.k));
        if (s.fulcrum) kids.push(S('rect', { x: x - 2, y: yt - 2, width: bw + 4, height: hh + 4, class: 'fulcrum-ring' }));
        const txt = s.txt || lab(s.raw);
        const lift = band < tw(txt, 10.5, true) + 4 && i % 2 ? 11 : 0;
        const above = s.kind === 'total' ? s.v >= 0 : true;
        kids.push(T(cx, (above ? yt - 4 : yt + hh + 10) + (above ? -lift : lift), txt, 'val' + (s.residual ? ' neg' : ''), 'middle'));
        if (s.fulcrum) kids.push(T(cx, yt - 15 - lift, 'Fulcrum', 'val fulcrum-w', 'middle'));
        if (s.residual) kids.push(T(cx, yt - 15 - lift, 'Residual', 'val neg', 'middle'));
        mark(ctx, { x, y: yt, w: bw, h: hh, label: s.residual ? 'Unexplained residual ' + s.raw + ': the stated total does not equal the steps before it' : itemName(s, s.label, p.title, sp.unit) + (s.fulcrum ? ', fulcrum class' : ''), desc: s.residual ? { t: 'note', kind: 'calculated', code: 'residual', title: 'Unexplained residual', sub: s.stated.label, fields: [['Residual', s.raw, true], ['Stated total', s.stated.raw, true]], note: 'The steps before this total do not add up to it. The difference is drawn as its own step instead of being hidden.', table: s.stated.desc && s.stated.desc.table ? { id: s.stated.desc.table, row: s.stated.desc.r, col: s.stated.desc.c } : null } : s.desc, kids });
      });
    });
    return Math.ceil(panels.length / grid.cols) * panelH;
  }

  /* ---------- engine: waterfall on its side (rows of steps; labels left, bars from the running total) ---------- */
  function waterfallH(ctx, sp, panels, sc0) {
    const W = ctx.W;
    const grid = gridLayout(W, panels.length, 330, 22);
    const sc = niceScale(sc0.lo, sc0.hi, grid.pw < 420 ? 3 : 4);
    const titleH = panels.some((p) => p.title) ? 20 : 0;
    const geo = panels.map((p) => {
      const LW = Math.max(104, Math.min(grid.pw * 0.42, 210));
      const rows = p.steps.map((s) => Math.max(22, wrapText(s.label, LW - 10, 11).length * 12 + 8));
      return { LW, rows, h: titleH + 6 + rows.reduce((a, b) => a + b, 0) + 22 };
    });
    const rowH = [];
    panels.forEach((p, pi) => {
      const r = Math.floor(pi / grid.cols);
      rowH[r] = Math.max(rowH[r] || 0, geo[pi].h);
    });
    const rowTop = rowH.map((h, i) => rowH.slice(0, i).reduce((a, b) => a + b + 10, 0));
    panels.forEach((p, pi) => {
      const g = geo[pi];
      const ox = (pi % grid.cols) * (grid.pw + grid.gap);
      const oy = rowTop[Math.floor(pi / grid.cols)];
      const L = ox + g.LW;
      const R = ox + grid.pw - 44;
      const top = oy + titleH + 6;
      const bot = top + g.rows.reduce((a, b) => a + b, 0);
      const x = lin(sc.lo, sc.hi, L, R);
      if (p.title) ctx.svg.appendChild(T(ox + 2, oy + 12, p.title, 'ttl'));
      axisH(ctx, sc, x, top, bot);
      let yy = top;
      const mids = [];
      p.steps.forEach((s, i) => {
        const rh = g.rows[i];
        const mid = yy + rh / 2;
        mids.push(mid);
        const lines = wrapText(s.label, g.LW - 10, 11);
        const t = S('text', { class: 'cat', x: L - 8, y: mid - ((lines.length - 1) * 12) / 2 + 4, 'text-anchor': 'end' });
        lines.forEach((ln, k) => t.appendChild(S('tspan', { x: L - 8, dy: k === 0 ? 0 : 12, text: ln })));
        ctx.svg.appendChild(t);
        yy += rh;
      });
      // connectors: the running total carries from one step's end to the next step
      p.steps.forEach((s, i) => {
        if (i === p.steps.length - 1) return;
        const xx = Math.round(x(s.to)) + 0.5;
        ctx.svg.appendChild(S('line', { class: 'conn', x1: xx, x2: xx, y1: mids[i] + 6, y2: mids[i + 1] - 6, 'aria-hidden': 'true' }));
      });
      p.steps.forEach((s, i) => {
        const mid = mids[i];
        const x0 = Math.min(x(s.from), x(s.to));
        const ww = Math.max(Math.abs(x(s.to) - x(s.from)), 1.5);
        const cls = s.cls || (s.kind === 'total' ? 'sr-2' : s.v >= 0 ? 'sr-0' : 'sr-1');
        const kids = [];
        if (s.residual) {
          ctx.seen.residual = true;
          kids.push(S('rect', { x: x0, y: mid - 6, width: ww, height: 12, class: 'sh sg-neg res' }));
        } else kids.push(shape(ctx, 'rect', { x: x0, y: mid - 6, width: ww, height: 12, class: s.dashed ? 'dashed' : '' }, cls, s.k));
        if (s.fulcrum) kids.push(S('rect', { x: x0 - 2, y: mid - 8, width: ww + 4, height: 16, class: 'fulcrum-ring' }));
        const txt = (s.txt || lab(s.raw)) + (s.fulcrum ? '  Fulcrum' : s.residual ? '  Residual' : '');
        const right = x0 + ww + 5;
        const fits = right + tw(txt, 10.5, true) <= ox + grid.pw;
        kids.push(T(fits ? right : x0 - 5, mid + 4, txt, 'val' + (s.residual ? ' neg' : s.fulcrum ? ' fulcrum-w' : ''), fits ? 'start' : 'end'));
        mark(ctx, { x: x0, y: mid - 6, w: ww, h: 12, label: s.residual ? 'Unexplained residual ' + s.raw + ': the stated total does not equal the steps before it' : itemName(s, s.label, p.title, sp.unit) + (s.fulcrum ? ', fulcrum class' : ''), desc: s.residual ? { t: 'note', kind: 'calculated', code: 'residual', title: 'Unexplained residual', sub: s.stated.label, fields: [['Residual', s.raw, true], ['Stated total', s.stated.raw, true]], note: 'The steps before this total do not add up to it. The difference is drawn as its own step instead of being hidden.', table: s.stated.desc && s.stated.desc.table ? { id: s.stated.desc.table, row: s.stated.desc.r, col: s.stated.desc.c } : null } : s.desc, kids });
      });
      if (sp.unit && pi === panels.length - 1) ctx.svg.appendChild(T(ox + grid.pw - 2, bot + 28, sp.unit, 'ax unit', 'end'));
    });
    return rowTop[rowTop.length - 1] + rowH[rowH.length - 1] + 14;
  }

  /* ---------- engine: bullets ---------- */
  /* a unit group's heading in words */
  const groupWord = (u) => ({ x: 'Ratios (x)', 'US$ m': 'Amounts (US$ m)', '% NAV': 'Share of NAV (%)', '%': 'Percentages' }[u] || u);
  function engineBullets(ctx, sp) {
    const W = ctx.W;
    // in a narrow slot the test's name sits above its track, so the track keeps the width and the name keeps one or two lines
    const stacked = W < 520;
    const LW = stacked ? 0 : Math.max(120, Math.min(W * 0.3, 230));
    const RW = stacked ? Math.max(92, Math.min(120, W * 0.26)) : Math.max(100, Math.min(150, W * 0.2));
    const L = stacked ? 2 : LW + 8;
    const R = W - RW - 6;
    const groups = [];
    sp.rows.forEach((r) => {
      let g = groups.find((x) => x.key === r.group);
      if (!g) groups.push((g = { key: r.group, label: r.groupLabel, rows: [] }));
      g.rows.push(r);
    });
    let yy = 4;
    groups.forEach((g) => {
      const vals = [];
      g.rows.forEach((r) => [r.cur, r.thr, r.proj].forEach((v) => v != null && !isNaN(v) && vals.push(v)));
      const gsc = sp.scale === 'row' ? null : niceScale(0, Math.max.apply(null, vals.concat([0])) * 1.08, 4);
      if (groups.length > 1 && g.label) {
        ctx.svg.appendChild(T(2, yy + 10, groupWord(g.label), 'ttl'));
        yy += 18;
      }
      const gTop = yy;
      g.rows.forEach((r) => {
        let mid;
        let rh;
        const sc = gsc || niceScale(0, Math.max(r.cur || 0, r.thr || 0, r.proj || 0) * 1.1 || 1, 3);
        const x = lin(sc.lo, sc.hi, L, R);
        if (stacked) {
          const lines = wrapText(r.label, W - 6, 11.5).slice(0, 3);
          const t = S('text', { class: 'cat strong', x: 0, y: yy + 12 });
          lines.forEach((ln, i) => t.appendChild(S('tspan', { x: 0, dy: i === 0 ? 0 : 13, text: ln })));
          // the test's kind follows its name on the last line when it fits, else on a line of its own
          const lastW = tw(lines[lines.length - 1], 11.5);
          const subInline = r.sub && lastW + tw(' · ' + r.sub, 10.5) < W - 6;
          if (subInline) t.appendChild(S('tspan', { class: 'cat sub', dx: 0, text: ' · ' + r.sub }));
          ctx.svg.appendChild(t);
          const labelH = lines.length * 13 + (r.sub && !subInline ? 12 : 0);
          if (r.sub && !subInline) ctx.svg.appendChild(T(0, yy + 12 + lines.length * 13, r.sub, 'cat sub'));
          mid = yy + labelH + 28;
          rh = labelH + (r.projI ? 60 : 48);
        } else {
          const lines = wrapText(r.label, LW - 8, 11.5);
          rh = Math.max(r.projI ? 58 : 46, lines.length * 13 + (r.sub ? 13 : 0) + 12);
          mid = yy + rh / 2 + 4;
          const t = S('text', { class: 'cat strong', x: 0, y: mid - ((lines.length - 1) * 13) / 2 - (r.sub ? 4 : 0) + 3 });
          lines.forEach((ln, i) => t.appendChild(S('tspan', { x: 0, dy: i === 0 ? 0 : 13, text: ln })));
          ctx.svg.appendChild(t);
          if (r.sub) ctx.svg.appendChild(T(0, mid + ((lines.length - 1) * 13) / 2 + 11, r.sub, 'cat sub'));
        }
        ctx.svg.appendChild(S('rect', { x: L, y: mid - 6, width: R - L, height: 12, class: 'trk' }));
        if (stacked && gsc) {
          const gt = S('g', { class: 'grid', 'aria-hidden': 'true' });
          gsc.ticks.forEach((tk) => gt.appendChild(S('line', { x1: Math.round(x(tk)) + 0.5, x2: Math.round(x(tk)) + 0.5, y1: mid - 9, y2: mid + 9, class: tk === 0 ? 'zero' : '' })));
          ctx.svg.appendChild(gt);
        }
        if (sp.scale === 'row') {
          ctx.svg.appendChild(T(L, mid + 19, '0', 'ax', 'start'));
          ctx.svg.appendChild(T(R, mid + 19, fmtTick(sc.hi, sc.step), 'ax', 'end'));
        }
        if (!isNaN(r.cur) && !isNaN(r.thr)) {
          const a = Math.min(x(r.cur), x(r.thr));
          const b = Math.max(x(r.cur), x(r.thr));
          ctx.svg.appendChild(S('rect', { x: a, y: mid - 6, width: Math.max(1, b - a), height: 12, class: 'band tn-' + r.tone + '-f', 'aria-hidden': 'true' }));
        }
        if (!isNaN(r.cur)) {
          const k = r.curI.k;
          mark(ctx, { x: x(0), y: mid - 4, w: Math.max(2, x(r.cur) - x(0)), h: 8, label: itemName(r.curI, r.curLabel || 'Current', r.label, r.unit), desc: r.curI.desc, kids: [shape(ctx, 'rect', { x: x(0), y: mid - 4, width: Math.max(2, x(r.cur) - x(0)), height: 8 }, 'sr-0', k), (x(r.cur) > L + 60 ? T(x(r.cur) - 3, mid + 17, lab(r.curI.raw), 'val', 'end') : T(x(r.cur) + 4, mid + 17, lab(r.curI.raw), 'val'))] });
        } else if (r.curI) gapMark(ctx, x(0) + 20, mid + 3, r.curI, r.curLabel || 'Current', r.label);
        if (!isNaN(r.thr)) {
          const tx = x(r.thr);
          mark(ctx, { x: tx - 1, y: mid - 12, w: 2, h: 24, label: itemName(r.thrI, r.thrLabel || (r.dir === 'Floor' ? 'Floor' : r.dir === 'Limit' ? 'Limit' : 'Ceiling'), r.label, r.unit), desc: r.thrI.desc, kids: [S('line', { x1: tx, x2: tx, y1: mid - 12, y2: mid + 12, class: 'rule-mk' }), T(tx, mid - 15, (r.dir === 'Floor' ? 'floor ' : r.dir === 'Limit' ? 'limit ' : 'ceiling ') + lab(r.thrI.raw), 'val thr', tx > R - 40 ? 'end' : tx < L + 40 ? 'start' : 'middle')] });
        }
        if (r.projI && !isNaN(r.proj)) {
          const px = x(r.proj);
          const d = 5;
          mark(ctx, { x: px - d, y: mid - d, w: d * 2, h: d * 2, label: itemName(r.projI, 'Projected', r.label, r.unit), desc: r.projI.desc, kids: [S('path', { d: 'M' + px + ' ' + (mid - d) + 'L' + (px + d) + ' ' + mid + 'L' + px + ' ' + (mid + d) + 'L' + (px - d) + ' ' + mid + 'Z', class: 'proj-dot' + (r.projBreach ? ' breach' : '') }), T(px + 8, mid + 29, lab(r.projI.raw), 'val')] });
        }
        // headroom word on the right
        const hx = R + 12;
        const kids = [icon(r.tone === 'neg' ? 'cross' : r.tone === 'cau' ? 'warn' : 'tick', hx, mid - 14, 13, 'tn-' + r.tone), T(hx + 17, mid - 3, r.word, 'wd tn-' + r.tone), T(hx + 17, mid + 10, r.headText, 'val')];
        if (r.projBreach) kids.push(T(hx + 17, mid + 22, 'Projected breach', 'wd tn-neg'));
        if (r.headI && r.headI.k === 'gap') gapMark(ctx, hx + 20, mid + 3, r.headI, 'Headroom', r.label);
        else mark(ctx, { x: hx - 2, y: mid - 16, w: RW - 10, h: r.projBreach ? 46 : 34, label: nm(r.label, r.word) + ': ' + r.headText + (r.headI && r.headI.word ? ', ' + r.headI.word : ''), desc: r.headI ? r.headI.desc : r.curI.desc, kids });
        yy += rh;
      });
      if (gsc && sp.scale !== 'row') {
        const ax = lin(gsc.lo, gsc.hi, L, R);
        axisH(ctx, gsc, ax, stacked ? yy : gTop, yy);
        yy += 24;
      }
    });
    if (sp.limited) ctx.notes.push(sp.limited);
    return yy + 6;
  }

  /* ---------- engine: dumbbells ---------- */
  function engineDumbbell(ctx, sp) {
    const W = ctx.W;
    const LW = Math.max(130, Math.min(W * 0.34, 270));
    const L = LW + 12;
    const R = W - 70;
    let dom = null;
    if (sp.shared) {
      const vals = [];
      sp.rows.forEach((r) => {
        if (r.a && !isNaN(r.a.v)) vals.push(r.a.v);
        if (r.b && !isNaN(r.b.v)) vals.push(r.b.v);
      });
      // a dumbbell encodes position, not length: the shared axis spans the values (padded), not zero to the maximum
      const vmin = Math.min.apply(null, vals);
      const vmax = Math.max.apply(null, vals.concat([1]));
      const span = vmax - vmin || Math.abs(vmax) || 1;
      dom = niceScale(vmin - span * 0.12, vmax + span * 0.12, 5, sp.zero === true);
    }
    let yy = 4;
    sp.rows.forEach((r) => {
      const lines = wrapText(r.label, LW - 8, 11.5);
      const rh = Math.max(32, lines.length * 13 + (r.sub ? 12 : 0) + 10);
      const mid = yy + rh / 2;
      const t = S('text', { class: 'cat' + (r.issuer ? ' strong' : ''), x: 0, y: mid - ((lines.length - 1) * 13) / 2 - (r.sub ? 4 : 0) + 4 });
      lines.forEach((ln, i) => t.appendChild(S('tspan', { x: 0, dy: i === 0 ? 0 : 13, text: ln })));
      ctx.svg.appendChild(t);
      if (r.sub) ctx.svg.appendChild(T(0, mid + ((lines.length - 1) * 13) / 2 + 12, r.sub, 'cat sub'));
      if (r.text) {
        mark(ctx, { x: L, y: mid - 12, w: R - L, h: 24, label: r.text.label, desc: r.text.desc, kids: [T(L, mid + 4, r.text.shown, 'cat sub')] });
        yy += rh;
        return;
      }
      let x;
      if (dom) x = lin(dom.lo, dom.hi, L, R);
      else {
        const vs = [r.a, r.b].filter((q) => q && !isNaN(q.v)).map((q) => q.v);
        const [d0, d1] = pad(Math.min.apply(null, vs), Math.max.apply(null, vs), 0.35);
        x = lin(d0, d1, L + 30, R - 30);
      }
      ctx.svg.appendChild(S('line', { class: 'trk-l', x1: L, x2: R, y1: mid, y2: mid, 'aria-hidden': 'true' }));
      const pa = r.a && !isNaN(r.a.v);
      const pb = r.b && !isNaN(r.b.v);
      if (pa && pb) ctx.svg.appendChild(S('line', { class: 'dumb-seg' + (r.issuer ? ' issuer' : ''), x1: x(r.a.v), x2: x(r.b.v), y1: mid, y2: mid, 'aria-hidden': 'true' }));
      const place = (q, which) => {
        if (!q) return;
        if (isNaN(q.v)) {
          gapMark(ctx, which === 'a' ? L + 24 : L + 70, mid + 4, q, r.aName && which === 'a' ? r.aName : r.bName, r.label);
          return;
        }
        const cx = x(q.v);
        const sname = which === 'a' ? r.aName : r.bName;
        const cls = which === 'a' ? r.aCls || 'sr-3' : r.issuer ? 'sr-0' : r.bCls || 'sr-1';
        const hollow = which === 'a' && r.aHollow;
        let sh;
        if (r.aSquare && which === 'a') sh = shape(ctx, 'rect', { x: cx - 4.5, y: mid - 4.5, width: 9, height: 9 }, cls, q.k);
        else if (hollow) {
          ctx.seen.solid = true;
          sh = S('circle', { cx, cy: mid, r: 5, class: 'ring ' + cls });
        } else sh = shape(ctx, 'circle', { cx, cy: mid, r: 5 }, cls, q.k);
        const other = which === 'a' ? (pb ? r.b.v : null) : pa ? r.a.v : null;
        const left = other == null ? true : q.v <= other;
        const kids = [sh, T(left ? cx - 9 : cx + 9, mid + 4, lab(q.raw), 'val', left ? 'end' : 'start')];
        mark(ctx, { x: cx - 5, y: mid - 5, w: 10, h: 10, label: itemName(q, sname, r.label, r.unit), desc: q.desc, kids });
      };
      place(r.a, 'a');
      place(r.b, 'b');
      if (r.right) ctx.svg.appendChild(T(W - 2, mid + 4, r.right, 'val', 'end'));
      yy += rh;
    });
    if (dom) {
      const ax = lin(dom.lo, dom.hi, L, R);
      axisH(ctx, dom, ax, 2, yy);
      if (sp.unit) ctx.svg.appendChild(T(R, yy + 28, sp.unit, 'ax unit', 'end'));
      return yy + 34;
    }
    return yy + 4;
  }

  /* ---------- engine: range strips ---------- */
  function engineRange(ctx, sp) {
    const W = ctx.W;
    const LW = Math.max(120, Math.min(W * 0.28, 230));
    const L = LW + 12;
    const R = W - 20;
    let dom = null;
    if (sp.shared) {
      const vs = [];
      sp.rows.forEach((r) => r.items.forEach((i) => !isNaN(i.v) && vs.push(i.v)));
      const [d0, d1] = pad(Math.min.apply(null, vs), Math.max.apply(null, vs), 0.06);
      dom = niceScale(d0, d1, 5, false);
    }
    let yy = 4;
    sp.rows.forEach((r) => {
      const lines = wrapText(r.label, LW - 8, 11.5);
      const rh = Math.max(46, lines.length * 13 + (r.sub ? 12 : 0) + 12);
      const mid = yy + rh / 2 + 2;
      const t = S('text', { class: 'cat strong', x: 0, y: mid - ((lines.length - 1) * 13) / 2 - (r.sub ? 4 : 0) + 3 });
      lines.forEach((ln, i) => t.appendChild(S('tspan', { x: 0, dy: i === 0 ? 0 : 13, text: ln })));
      ctx.svg.appendChild(t);
      if (r.sub) ctx.svg.appendChild(T(0, mid + ((lines.length - 1) * 13) / 2 + 11, r.sub, 'cat sub'));
      const vs = r.items.filter((i) => !isNaN(i.v)).map((i) => i.v);
      let x;
      if (dom) x = lin(dom.lo, dom.hi, L, R);
      else {
        const [d0, d1] = pad(Math.min.apply(null, vs), Math.max.apply(null, vs), 0.12);
        x = lin(d0, d1, L + 24, R - 24);
      }
      ctx.svg.appendChild(S('line', { class: 'trk-l', x1: L, x2: R, y1: mid, y2: mid, 'aria-hidden': 'true' }));
      const by = (role) => r.items.find((i) => i.role === role);
      const lo = by(r.style === 'peer' ? 'min' : 'low');
      const hi = by(r.style === 'peer' ? 'max' : 'high');
      const q1 = by('q1');
      const q3 = by('q3');
      const mdn = by(r.style === 'peer' ? 'median' : 'mid');
      const ok = (i) => i && !isNaN(i.v);
      if (ok(lo) && ok(hi)) ctx.svg.appendChild(S('line', { class: 'whisk', x1: x(lo.v), x2: x(hi.v), y1: mid, y2: mid, 'aria-hidden': 'true' }));
      if (r.style === 'peer' && ok(q1) && ok(q3)) ctx.svg.appendChild(shape(ctx, 'rect', { x: x(q1.v), y: mid - 7, width: Math.max(1, x(q3.v) - x(q1.v)), height: 14 }, 'sr-6', q1.k));
      if (r.style === 'range' && ok(lo) && ok(hi)) ctx.svg.appendChild(shape(ctx, 'rect', { x: x(lo.v), y: mid - 7, width: Math.max(1, x(hi.v) - x(lo.v)), height: 14 }, 'sr-6', lo.k));
      const rangeGap = r.items.filter((i) => i.role !== 'dot' && isNaN(i.v));
      if (rangeGap.length) gapMark(ctx, L + 22, mid + 4, rangeGap[0], r.rangeName || 'Range', r.label);
      r.items.forEach((i) => {
        if (isNaN(i.v)) return;
        const cx = x(i.v);
        const kids = [];
        let nameS = i.nameS;
        if (i.role === 'dot') {
          kids.push(shape(ctx, 'circle', { cx, cy: mid, r: 5.5 }, r.dotCls || 'sr-0', i.k));
          kids.push(T(cx, mid - 11, lab(i.raw), 'val dotv', 'middle'));
        } else if (i.role === 'min' || i.role === 'max' || i.role === 'low' || i.role === 'high') {
          kids.push(S('line', { class: 'cap', x1: cx, x2: cx, y1: mid - 7, y2: mid + 7 }));
          const left = i.role === 'min' || i.role === 'low';
          kids.push(T(left ? cx - 4 : cx + 4, mid + 22, lab(i.raw), 'val', left ? 'end' : 'start'));
        } else if (i.role === 'median' || i.role === 'mid') {
          kids.push(S('line', { class: 'med', x1: cx, x2: cx, y1: mid - 9, y2: mid + 9 }));
          kids.push(T(cx, mid + 22, lab(i.raw), 'val', 'middle'));
        } else {
          kids.push(S('line', { class: 'cap q', x1: cx, x2: cx, y1: mid - 7, y2: mid + 7 }));
        }
        mark(ctx, { x: cx - 4, y: mid - 8, w: 8, h: 16, label: itemName(i, nameS, r.label, r.unit), desc: i.desc, kids });
      });
      yy += rh;
    });
    if (dom) {
      const ax = lin(dom.lo, dom.hi, L, R);
      axisH(ctx, dom, ax, 2, yy);
      if (sp.unit) ctx.svg.appendChild(T(R, yy + 28, sp.unit, 'ax unit', 'end'));
      return yy + 34;
    }
    return yy + 4;
  }

  /* ---------- engine: lines (small multiples) ---------- */
  function engineLines(ctx, sp) {
    const W = ctx.W;
    const grid = gridLayout(W, sp.panels.length, sp.minPanelW || 240, 14);
    const plotH = ctx.opts.compact ? 90 : sp.plotH || 120;
    const panelH = 24 + plotH + 30;
    const nC = sp.cats.length;
    const divider = sp.divider; // index of first projected category, or -1
    sp.panels.forEach((p, pi) => {
      const ox = (pi % grid.cols) * (grid.pw + grid.gap);
      const oy = Math.floor(pi / grid.cols) * panelH;
      const L = ox + 40;
      const vals = [];
      p.series.forEach((s) => s.pts.forEach((q) => !isNaN(q.v) && vals.push(q.v)));
      // a series that reaches the last period is labelled at its end, in a gutter right of the plot
      const lastLabels = p.series.map((s) => s.pts.filter((q) => !isNaN(q.v)).pop()).filter(Boolean);
      const gutter = lastLabels.some((q) => q.i === nC - 1) ? Math.max.apply(null, lastLabels.map((q) => tw(lab(q.raw), 10.5, true))) + 10 : 0;
      const R = ox + grid.pw - Math.max(12, gutter);
      const top = oy + 24;
      const bot = top + plotH;
      const sc = niceScale(Math.min.apply(null, vals.concat([0])), Math.max.apply(null, vals.concat([0])), 3);
      const y = lin(sc.lo, sc.hi, bot, top);
      const band = (R - L) / nC;
      const xAt = (i) => L + band * (i + 0.5);
      ctx.svg.appendChild(T(ox + 2, oy + 12, p.title, 'ttl'));
      if (p.unit) ctx.svg.appendChild(T(ox + grid.pw - 2, oy + 12, p.unit, 'ax unit', 'end'));
      axisV(ctx, sc, y, L, R);
      // in a tight band the fiscal-year prefix is written once: FY23 24 25 LTM PF 26E
      const firstFY = sp.cats.findIndex((c) => /^FY\d\d$/.test(c.short));
      const tight = band < 36;
      sp.cats.forEach((c, i) => ctx.svg.appendChild(T(xAt(i), bot + 14, tight && i > firstFY && firstFY >= 0 && /^FY\d\d$/.test(c.short) ? c.short.slice(2) : c.short, 'ax cx', 'middle')));
      if (divider != null && divider > 0 && divider < nC) {
        const dx = L + band * divider;
        ctx.svg.appendChild(S('line', { class: 'divider', x1: dx, x2: dx, y1: top - 10, y2: bot, 'aria-hidden': 'true' }));
        // the divider's word sits above the plot, clear of the data labels
        ctx.svg.appendChild(T(dx + 3, top - 3, 'Projected', 'ax proj-w'));
        ctx.seen.proj = true;
      }
      p.series.forEach((s) => {
        const runs = [];
        let cur = [];
        if (s.from && !isNaN(s.from.v)) cur.push({ i: s.from.i, v: s.from.v, anchor: true });
        s.pts.forEach((q) => {
          if (isNaN(q.v)) {
            if (cur.length > 1 || (cur.length === 1 && !cur[0].anchor)) runs.push(cur);
            cur = [];
          } else cur.push(q);
        });
        if (cur.length > 1 || (cur.length === 1 && !cur[0].anchor)) runs.push(cur);
        runs.forEach((run) => {
          if (run.length < 2) return;
          ctx.svg.appendChild(S('polyline', { class: 'ln ' + s.cls + (s.proj ? ' proj' : ''), points: run.map((q) => xAt(q.i).toFixed(1) + ',' + y(q.v).toFixed(1)).join(' '), fill: 'none', 'aria-hidden': 'true' }));
        });
      });
      const ends = [];
      p.series.forEach((s, si) => {
        const last = s.pts.filter((q) => !isNaN(q.v)).pop();
        s.pts.forEach((q) => {
          const cx = xAt(q.i);
          const cat = sp.cats[q.i].full;
          if (isNaN(q.v)) {
            // in a tight band neighbouring gaps alternate height, so each n/a stays legible on its own period
            gapMark(ctx, cx, bot - (tight && q.i % 2 ? 24 : 10), q, s.label, cat);
            return;
          }
          const cy = y(q.v);
          const kids = [s.proj ? (ctx.seen.proj = true) && S('circle', { cx, cy, r: 3.6, class: 'ring ' + s.cls }) : shape(ctx, 'circle', { cx, cy, r: 3.6 }, s.cls, q.k)];
          const g = mark(ctx, { x: cx - 4, y: cy - 4, w: 8, h: 8, label: itemName(q, s.label, cat, p.unit) + (s.proj ? ', projected' : ''), desc: q.desc, kids });
          if (q === last) {
            // at the last period the label goes right of the point, in the gutter; earlier (the last reported value
            // before a projection) it sits above-left of the point, clear of the lines that leave it
            if (q.i === nC - 1) ends.push({ g, x: cx + 7, y: cy + 4, text: lab(q.raw) });
            else g.appendChild(T(cx - 5, cy - 6, lab(q.raw), 'val', 'end'));
          }
        });
      });
      // gutter labels never sit on each other: 12px apart, kept inside the plot's height
      ends.sort((a, b) => a.y - b.y);
      for (let k = 1; k < ends.length; k++) if (ends[k].y - ends[k - 1].y < 12) ends[k].y = ends[k - 1].y + 12;
      for (let k = ends.length - 1; k >= 0; k--) {
        const maxY = k === ends.length - 1 ? bot + 4 : ends[k + 1].y - 12;
        if (ends[k].y > maxY) ends[k].y = maxY;
      }
      ends.forEach((e) => e.g.appendChild(T(e.x, Math.max(top + 4, e.y), e.text, 'val', 'start')));
    });
    return Math.ceil(sp.panels.length / grid.cols) * panelH;
  }

  /* ---------- engine: scatter (spread against maturity) ---------- */
  const SHAPES = ['circle', 'square', 'diamond', 'triangle', 'cross'];
  function pointShape(ctx, kind, x, y, r, cls, k, filled) {
    const a = filled ? shapeAttrs(ctx, cls, k) : { class: 'ring ' + cls };
    if (!filled) ctx.seen.solid = true;
    switch (kind) {
      case 'square': return S('rect', Object.assign({ x: x - r * 0.9, y: y - r * 0.9, width: r * 1.8, height: r * 1.8 }, a));
      case 'diamond': return S('path', Object.assign({ d: 'M' + x + ' ' + (y - r * 1.25) + 'L' + (x + r * 1.25) + ' ' + y + 'L' + x + ' ' + (y + r * 1.25) + 'L' + (x - r * 1.25) + ' ' + y + 'Z' }, a));
      case 'triangle': return S('path', Object.assign({ d: 'M' + x + ' ' + (y - r * 1.2) + 'L' + (x + r * 1.15) + ' ' + (y + r * 0.9) + 'L' + (x - r * 1.15) + ' ' + (y + r * 0.9) + 'Z' }, a));
      case 'cross': return S('path', Object.assign({ d: 'M' + (x - r) + ' ' + (y - r) + 'L' + (x + r) + ' ' + (y + r) + 'M' + (x + r) + ' ' + (y - r) + 'L' + (x - r) + ' ' + (y + r) }, a, { class: 'xmark ' + cls }));
      default: return S('circle', Object.assign({ cx: x, cy: y, r }, a));
    }
  }
  const shapeAttrs = (ctx, cls, k) => paintAttrs(ctx, cls, k);
  function engineScatter(ctx, sp) {
    const W = ctx.W;
    const plotH = ctx.opts.compact ? 150 : 210;
    const L = 46;
    const R = W - 14;
    const top = 26;
    const bot = top + plotH;
    const ds = sp.points.filter((p) => !isNaN(p.x)).map((p) => p.x);
    const d0 = Math.min.apply(null, ds) - 90 * 864e5;
    const d1 = Math.max.apply(null, ds) + 90 * 864e5;
    const x = lin(d0, d1, L, R);
    const vs = sp.points.filter((p) => !isNaN(p.v)).map((p) => p.v);
    const sc = niceScale(0, Math.max.apply(null, vs.concat([1])) * 1.1, 4);
    const y = lin(sc.lo, sc.hi, bot, top);
    axisV(ctx, sc, y, L, R);
    // the unit heads the value axis, above its top tick
    ctx.svg.appendChild(T(L - 6, top - 12, 'bps', 'ax unit', 'end'));
    const gx = S('g', { class: 'grid', 'aria-hidden': 'true' });
    for (let yr = new Date(d0).getUTCFullYear() + 1; yr <= new Date(d1).getUTCFullYear(); yr++) {
      const xx = Math.round(x(Date.UTC(yr, 0, 1))) + 0.5;
      gx.appendChild(S('line', { x1: xx, x2: xx, y1: top, y2: bot }));
      gx.appendChild(T(xx, bot + 13, String(yr), 'ax', 'middle'));
    }
    ctx.svg.appendChild(gx);
    const placed = [];
    sp.points.forEach((p) => {
      const sname = sp.series[p.s].label;
      if (isNaN(p.x)) return;
      const cx = x(p.x);
      if (isNaN(p.v)) {
        gapMark(ctx, cx, bot - 12, p, sname, p.name);
        return;
      }
      const cy = y(p.v);
      const kids = [pointShape(ctx, SHAPES[p.s % SHAPES.length], cx, cy, 5, sp.series[p.s].cls, p.k, p.issuer)];
      if (p.issuer) {
        // an issuer point is named beside it: right of the point, or left of it near the right edge
        const txt = p.short;
        const w = tw(txt, 10.5);
        let done = false;
        for (const side of [1, -1]) {
          for (const dy of [0, -13, 13, -26, 26]) {
            const x0 = side > 0 ? cx + 9 : cx - 9 - w;
            const bx = { x0, x1: x0 + w, y0: cy + dy - 8, y1: cy + dy + 3 };
            if (bx.x1 > W || bx.x0 < L) continue;
            if (placed.some((q) => bx.x0 < q.x1 && bx.x1 > q.x0 && bx.y0 < q.y1 && bx.y1 > q.y0)) continue;
            placed.push(bx);
            kids.push(T(side > 0 ? cx + 9 : cx - 9, cy + dy, txt, 'val lbl', side > 0 ? 'start' : 'end'));
            done = true;
            break;
          }
          if (done) break;
        }
      }
      mark(ctx, { x: cx - 5, y: cy - 5, w: 10, h: 10, label: nm(p.name, sname) + ': ' + p.xText + ', ' + withUnit(p.raw, 'bps') + (p.word ? ', ' + p.word : '') + (p.issuer ? ', issuer' : ''), desc: p.desc, kids });
    });
    return bot + 22;
  }

  /* ---------- engine: risk matrix ---------- */
  function engineMatrix(ctx, sp) {
    const W = ctx.W;
    const LW = 74;
    const cw = Math.min(120, (W - LW - 10) / sp.cols.length);
    const ch = 64;
    const top = 30;
    sp.cols.forEach((c, ci) => ctx.svg.appendChild(T(LW + cw * (ci + 0.5), top - 6, c, 'cat strong', 'middle')));
    ctx.svg.appendChild(T(0, 9, 'Impact down the side, probability across', 'ax'));
    sp.rows.forEach((rw, ri) => {
      ctx.svg.appendChild(T(LW - 8, top + ch * ri + ch / 2 + 4, rw, 'cat strong', 'end'));
      sp.cols.forEach((c, ci) => {
        const score = sp.rows.length - 1 - ri + ci; // 0..(n-1)*2
        const step = Math.min(4, Math.round((score / ((sp.rows.length - 1 + sp.cols.length - 1) || 1)) * 4));
        ctx.svg.appendChild(S('rect', { x: LW + cw * ci + 1, y: top + ch * ri + 1, width: cw - 2, height: ch - 2, class: 'mx mx-' + step, 'aria-hidden': 'true' }));
      });
    });
    sp.cells.forEach((cell) => {
      cell.chips.forEach((chip, k) => {
        const per = Math.max(1, Math.floor((cw - 8) / 46));
        const cx0 = LW + cw * cell.c + 6 + (k % per) * 46;
        const cy0 = top + ch * cell.r + 6 + Math.floor(k / per) * 26;
        const kids = [S('rect', { x: cx0, y: cy0, width: 42, height: 20, class: 'chip' + (chip.k === 'soft' ? ' soft' : '') }), T(cx0 + 21, cy0 + 14, chip.raw, 'val', 'middle')];
        if (chip.k === 'soft') ctx.seen.soft = true;
        else ctx.seen.solid = true;
        mark(ctx, { x: cx0, y: cy0, w: 42, h: 20, label: nm(chip.raw, 'impact ' + chip.impact, 'probability ' + chip.prob) + (chip.word ? ', ' + chip.word : ''), desc: chip.desc, kids });
      });
    });
    return top + ch * sp.rows.length + 4;
  }

  /* ---------- engine: tornado ---------- */
  function engineTornado(ctx, sp) {
    const W = ctx.W;
    const rows = sp.rows.filter((r) => !isNaN(r.i.v)).sort((a, b) => Math.abs(b.i.v) - Math.abs(a.i.v));
    const gaps = sp.rows.filter((r) => isNaN(r.i.v));
    const all = rows.concat(gaps);
    const LW = Math.max(130, Math.min(W * 0.36, 280));
    const L = LW + 12;
    const R = W - 52;
    const vs = rows.map((r) => r.i.v);
    const sc = niceScale(Math.min.apply(null, vs.concat([0])) * 1.08, Math.max.apply(null, vs.concat([0])) * 1.08, 5);
    const x = lin(sc.lo, sc.hi, L, R);
    const heights = all.map((r) => Math.max(28, wrapText(r.label, LW - 8, 11.5).length * 13 + (r.sub ? 12 : 0) + 8));
    const bot = 4 + heights.reduce((a, b) => a + b, 0);
    axisH(ctx, sc, x, 4, bot);
    let yy = 4;
    all.forEach((r, i) => {
      const rh = heights[i];
      const mid = yy + rh / 2;
      const lines = wrapText(r.label, LW - 8, 11.5);
      const t = S('text', { class: 'cat', x: 0, y: mid - ((lines.length - 1) * 13) / 2 - (r.sub ? 4 : 0) + 4 });
      lines.forEach((ln, k) => t.appendChild(S('tspan', { x: 0, dy: k === 0 ? 0 : 13, text: ln })));
      ctx.svg.appendChild(t);
      if (r.sub) ctx.svg.appendChild(T(0, mid + ((lines.length - 1) * 13) / 2 + 12, r.sub, 'cat sub'));
      const it = r.i;
      if (isNaN(it.v)) gapMark(ctx, x(0) + 20, mid + 4, it, 'Impact', r.label);
      else {
        const neg = it.v < 0;
        const xl = Math.min(x(0), x(it.v));
        const ww = Math.max(Math.abs(x(it.v) - x(0)), 1.5);
        mark(ctx, { x: xl, y: mid - 8, w: ww, h: 16, label: itemName(it, neg ? 'Adverse' : 'Favourable', r.label + (r.sub ? ' (' + r.sub + ')' : ''), ''), desc: it.desc, kids: [shape(ctx, 'rect', { x: xl, y: mid - 8, width: ww, height: 16 }, neg ? 'sr-1' : 'sr-0', it.k), neg ? T(xl - 4, mid + 4, lab(it.raw), 'val', 'end') : T(xl + ww + 4, mid + 4, lab(it.raw), 'val')] });
      }
      yy += rh;
    });
    if (sp.unit) ctx.svg.appendChild(T(R, bot + 28, sp.unit, 'ax unit', 'end'));
    return bot + 34;
  }

  /* ---------- engine: debt stack (cumulative staircase by rank) ---------- */
  function engineStack(ctx, sp) {
    const W = ctx.W;
    const LW = Math.max(130, Math.min(W * 0.3, 250));
    const L = LW + 10;
    const R = W - 16;
    const top = 38;
    const heights = sp.rows.map((r) => Math.max(18, wrapText(r.label, LW - 8, 11).length * 12 + 6));
    const bot = top + heights.reduce((a, b) => a + b, 0);
    const maxV = Math.max(sp.total || 0, sp.ev || 0, sp.cum) * 1.04;
    const x = lin(0, maxV, L, R);
    const g = S('g', { class: 'grid', 'aria-hidden': 'true' });
    if (sp.perX) {
      for (let m = 0; m * sp.perX <= maxV; m++) {
        const xx = Math.round(x(m * sp.perX)) + 0.5;
        g.appendChild(S('line', { x1: xx, x2: xx, y1: top, y2: bot, class: m === 0 ? 'zero' : '' }));
        g.appendChild(T(xx, bot + 13, m + 'x', 'ax', 'middle'));
      }
    } else {
      const sc = niceScale(0, maxV, 5);
      sc.ticks.forEach((t) => {
        const xx = Math.round(x(t)) + 0.5;
        g.appendChild(S('line', { x1: xx, x2: xx, y1: top, y2: bot, class: t === 0 ? 'zero' : '' }));
        g.appendChild(T(xx, bot + 13, fmtTick(t, sc.step), 'ax', 'middle'));
      });
    }
    ctx.svg.appendChild(g);
    let yy = top;
    let cum = 0;
    sp.rows.forEach((r, i) => {
      const rh = heights[i];
      const mid = yy + rh / 2;
      const lines = wrapText(r.label, LW - 8, 11);
      const t = S('text', { class: 'cat', x: LW - 6, y: mid - ((lines.length - 1) * 12) / 2 + 4, 'text-anchor': 'end' });
      lines.forEach((ln, k) => t.appendChild(S('tspan', { x: LW - 6, dy: k === 0 ? 0 : 12, text: ln })));
      ctx.svg.appendChild(t);
      const it = r.i;
      if (isNaN(it.v)) gapMark(ctx, x(cum) + 20, mid + 4, it, r.rank, r.label);
      else {
        const x0 = x(cum);
        const ww = Math.max(2, x(cum + it.v) - x0);
        mark(ctx, { x: x0, y: mid - 6, w: ww, h: 12, label: itemName(it, r.rank, r.label, 'US$ m'), desc: it.desc, kids: [shape(ctx, 'rect', { x: x0, y: mid - 6, width: ww, height: 12 }, r.cls, it.k), T(x0 + ww + 4 > R - 30 ? x0 - 4 : x0 + ww + 4, mid + 4, lab(it.raw), 'val', x0 + ww + 4 > R - 30 ? 'end' : 'start')] });
        cum += it.v;
      }
      yy += rh;
    });
    // rule markers: secured, total, EV (labels staggered)
    sp.rules.forEach((rl, i) => {
      if (isNaN(rl.i.v)) return;
      const xx = x(rl.i.v);
      const ly = 10 + (i % 3) * 11;
      mark(ctx, { x: xx - 1, y: top - 6, w: 2, h: bot - top + 6, label: nm(rl.name, withUnit(rl.i.raw, 'US$ m'), rl.mult ? rl.mult + ' of EBITDA' : '', rl.i.word), desc: rl.i.desc, kids: [S('line', { x1: xx, x2: xx, y1: ly + 2, y2: bot, class: 'rule-mk' + (rl.dash ? ' dash' : '') }), T(xx - 4, ly, rl.name + (rl.mult ? ' ' + rl.mult : ''), 'val thr', 'end')] });
    });
    ctx.svg.appendChild(T(R, bot + 28, sp.perX ? 'x EBITDA (bars are US$ m as served)' : 'US$ m', 'ax unit', 'end'));
    return bot + 34;
  }

  /* ---------- series and rank colours ---------- */
  function rankPref(rank) {
    const r = String(rank).toLowerCase();
    if (/unsecured/.test(r)) return 1;
    if (/second lien|2l/.test(r)) return 2;
    if (/super/.test(r)) return 6;
    if (/secured|first lien|1l/.test(r)) return 0;
    return 3;
  }
  function rankSeries(ranks) {
    const used = new Set();
    const spare = [4, 5, 7, 3, 6, 2];
    return ranks.map((rk) => {
      let i = rankPref(rk);
      if (used.has(i)) i = spare.find((s) => !used.has(s)) || 5;
      used.add(i);
      return { label: rk, cls: 'sr-' + i };
    });
  }
  const seriesN = (names) => names.map((n, i) => ({ label: n, cls: 'sr-' + [0, 1, 2, 3, 4, 5, 6, 7][i % 8] }));
  const seriesFromAll = (names) => names.map((n, i) => ({ label: n, cls: 'sr-' + (i % 8) }));
  const uniq = (a) => Array.from(new Set(a));
  const cell = (t, r, name) => t.rows[r][colIdx(t, name)];
  const cap0 = (s) => String(s).charAt(0).toUpperCase() + String(s).slice(1);
  const cap1 = (s) => String(s).charAt(0).toUpperCase() + String(s).slice(1).toLowerCase();
  const issuerTokens = (ctx) => {
    const set = new Set();
    const meta = WB.runMeta(WB.run);
    if (meta.issuerId) set.add(meta.issuerId);
    const cs = WB.table('snapshot.capital_structure');
    if (cs) {
      const fi = cs.columns.indexOf('facility');
      cs.rows.forEach((r) => {
        const m = /^([A-Z]{2,})\b/.exec(String(r[fi < 0 ? 0 : fi]));
        if (m) set.add(m[1]);
      });
    }
    return set;
  };
  const isIssuer = (ctx, name) => {
    const m = /^([A-Z]{2,})\b/.exec(String(name).trim());
    return !!m && issuerTokens(ctx).has(m[1]);
  };

  /* ---------- builders: one per chart_id ---------- */
  const BUILD = {};

  function stackedAgg(ctx, t, catCol, serCol, valCol, o) {
    const cats = uniq(t.rows.map((r, i) => cell(t, i, catCol)));
    const sers = uniq(t.rows.map((r, i) => cell(t, i, serCol)));
    const series = o.series ? o.series(sers) : seriesN(sers);
    const outCats = cats.map((cv) => {
      const items = [];
      let totalRows = [];
      series.forEach((s, si) => {
        const rows = t.rows.map((r, i) => i).filter((i) => cell(t, i, catCol) === cv && cell(t, i, serCol) === sers[si]);
        if (!rows.length) return;
        const its = rows.map((r) => item(ctx, t, r, valCol));
        const bad = its.find((q) => isNaN(q.v));
        if (bad) {
          items.push(Object.assign({}, bad, { s: si }));
          return;
        }
        totalRows = totalRows.concat(rows);
        const sum = sumExact(its.map((q) => q.raw));
        const w = worst(its);
        const title = (o.serLabel ? o.serLabel(sers[si]) : sers[si]) + ', ' + cv;
        items.push({ s: si, v: sum.n, raw: sum.text, k: w.k, word: w.word, desc: rows.length === 1 ? its[0].desc : aggDesc(t, rows, title, o.what || 'Sum', 'Sum', sum.text), extra: rows.length > 1 ? 'sum of ' + rows.length + ' rows' : '' });
      });
      const vals = items.filter((q) => !isNaN(q.v));
      const tot = vals.length ? sumExact(vals.map((q) => q.raw)) : null;
      return { label: o.catLabel ? o.catLabel(cv) : cv, items, total: tot ? tot.text : null };
    });
    return { series, cats: outCats };
  }

  BUILD['chart.maturity_wall'] = (ctx) => {
    const t = twinOf(ctx, 'model.maturity_wall');
    const a = stackedAgg(ctx, t, 'fiscal_year', 'rank', 'amount', { series: rankSeries, catLabel: (c) => c });
    ctx.legend = a.series.map((s) => ({ kind: 'fill', cls: s.cls, label: s.label }));
    ctx.unit = 'US$ m';
    return { engine: engineColumns, sp: { orient: 'v', mode: 'stack', series: a.series, panels: [{ cats: a.cats }], unit: 'US$ m' } };
  };
  BUILD['chart.liquidity_sources'] = (ctx) => {
    const t = twinOf(ctx, 'cp2d.liquidity_sources');
    const a = stackedAgg(ctx, t, 'accessible', 'component', 'amount', { catLabel: (c) => (c === 'Yes' ? 'Accessible' : c === 'No' ? 'Not accessible' : c), series: (names) => seriesFromAll(names) });
    ctx.legend = a.series.map((s) => ({ kind: 'fill', cls: s.cls, label: s.label }));
    return { engine: engineColumns, sp: { orient: 'v', mode: 'stack', series: a.series, panels: [{ cats: a.cats }], unit: 'US$ m', minPanelW: 280 } };
  };
  BUILD['chart.cash_uses'] = (ctx) => {
    const t = twinOf(ctx, 'cp2d.cash_uses_12m');
    const a = stackedAgg(ctx, t, 'timing', 'mandatory', 'amount', { series: (names) => names.map((n, i) => ({ label: n === 'Yes' ? 'Mandatory' : n === 'No' ? 'Not mandatory' : n, cls: n === 'Yes' ? 'sr-2' : 'sr-6' })) });
    ctx.legend = a.series.map((s) => ({ kind: 'fill', cls: s.cls, label: s.label }));
    return { engine: engineColumns, sp: { orient: 'v', mode: 'stack', series: a.series, panels: [{ cats: a.cats }], unit: 'US$ m' } };
  };
  BUILD['chart.issue_counts'] = (ctx) => {
    const t = twinOf(ctx, 'cp5.findings');
    const order = ['High', 'Medium', 'Low'];
    const sev = order.filter((s) => t.rows.some((r, i) => cell(t, i, 'severity') === s)).concat(uniq(t.rows.map((r, i) => cell(t, i, 'severity'))).filter((s) => !order.includes(s)));
    const mods = uniq(t.rows.map((r, i) => cell(t, i, 'module_id')));
    const cls = { High: 'sr-2', Medium: 'sr-0', Low: 'sr-6' };
    const series = sev.map((s, i) => ({ label: s, cls: cls[s] || 'sr-' + (3 + i) }));
    const cats = mods.map((m) => {
      const items = [];
      series.forEach((s, si) => {
        const rows = t.rows.map((r, i) => i).filter((i) => cell(t, i, 'module_id') === m && cell(t, i, 'severity') === s.label);
        if (!rows.length) return;
        items.push({ s: si, v: rows.length, raw: String(rows.length), k: 'solid', word: 'counted by the host', desc: aggDesc(t, rows, s.label + ' findings, ' + m, 'Count', String(rows.length), 'Count'), t, r: rows[0], col: 'severity' });
      });
      return { label: m, items, total: items.length > 1 ? String(items.reduce((a, q) => a + q.v, 0)) : null };
    });
    ctx.legend = series.map((s) => ({ kind: 'fill', cls: s.cls, label: s.label + ' severity' }));
    return { engine: engineColumns, sp: { orient: 'v', mode: 'stack', series, panels: [{ cats }], unit: 'findings', minPanelW: 300, integer: true } };
  };
  BUILD['chart.topic_counts'] = (ctx) => {
    const t = twinOf(ctx, 'cpl10.screen_topics');
    const fams = uniq(t.rows.map((r, i) => cell(t, i, 'family')));
    const disp = uniq(t.rows.map((r, i) => cell(t, i, 'disposition')));
    const series = seriesN(disp);
    const mats = ['High', 'Medium', 'Low'];
    const panels = fams.map((f) => ({
      title: f,
      cats: mats.map((m) => {
        const items = [];
        series.forEach((s, si) => {
          const rows = t.rows.map((r, i) => i).filter((i) => cell(t, i, 'family') === f && cell(t, i, 'materiality') === m && cell(t, i, 'disposition') === s.label);
          if (!rows.length) return;
          items.push({ s: si, v: rows.length, raw: String(rows.length), k: 'solid', word: 'counted by the host', desc: aggDesc(t, rows, s.label + ', ' + m + ' materiality, ' + f, 'Count', String(rows.length), 'Count'), t, r: rows[0], col: 'disposition' });
        });
        return { label: m, items, total: items.length ? String(items.reduce((a, q) => a + q.v, 0)) : null };
      }),
    }));
    ctx.legend = series.map((s) => ({ kind: 'fill', cls: s.cls, label: s.label }));
    return { engine: engineColumns, sp: { orient: 'v', mode: 'stack', series, panels, unit: 'topics', minPanelW: 200, plotH: 110, integer: true } };
  };
  BUILD['chart.basket_capacity'] = (ctx) => {
    const t = twinOf(ctx, 'cp4.capacity_register');
    const series = [{ label: 'Used', cls: 'sr-2' }, { label: 'Remaining', cls: 'sr-0' }];
    const cats = t.rows.map((r, i) => ({ label: cell(t, i, 'basket'), items: [Object.assign(item(ctx, t, i, 'used'), { s: 0 }), Object.assign(item(ctx, t, i, 'remaining'), { s: 1 })] }));
    ctx.legend = series.map((s) => ({ kind: 'fill', cls: s.cls, label: s.label }));
    return { engine: engineColumns, sp: { orient: 'h', mode: 'stack', series, panels: [{ cats }], unit: 'US$ m' } };
  };
  BUILD['chart.funding_gap'] = (ctx) => {
    const t = twinOf(ctx, 'cp3c.maturity_pressure');
    const series = [{ label: 'Maturing, covered by sources', cls: 'sr-0' }, { label: 'Funding gap', cls: 'sg-neg' }];
    const cats = t.rows.map((r, i) => {
      const mat = item(ctx, t, i, 'maturing_amount');
      const gap = item(ctx, t, i, 'funding_gap');
      const src = item(ctx, t, i, 'sources_available');
      const covered = !isNaN(mat.v) && !isNaN(gap.v) ? Object.assign({}, mat, { s: 0, v: mat.v - gap.v, raw: fmtComputed(mat.v - gap.v, Math.max(decimals(mat.raw), decimals(gap.raw))), extra: 'maturing amount less the funding gap' }) : Object.assign({}, mat, { s: 0 });
      return { label: cell(t, i, 'fiscal_year'), items: [covered, Object.assign(gap, { s: 1 })], total: null, rule: Object.assign(src, { label: 'Sources available' }) };
    });
    ctx.legend = series.map((s) => ({ kind: 'fill', cls: s.cls, label: s.label })).concat([{ kind: 'rule', label: 'Sources available' }]);
    return { engine: engineColumns, sp: { orient: 'v', mode: 'stack', series, panels: [{ cats }], unit: 'US$ m' } };
  };
  BUILD['chart.lme_exposure'] = (ctx) => {
    const t = twinOf(ctx, 'cp3c.creditor_exposure');
    const classes = uniq(t.rows.map((r, i) => cell(t, i, 'creditor_class')));
    const cases = uniq(t.rows.map((r, i) => cell(t, i, 'case_name')));
    const series = seriesN(cases);
    const cats = classes.map((c) => ({
      label: c,
      items: cases.map((cs, si) => {
        const r = t.rows.findIndex((_, i) => cell(t, i, 'creditor_class') === c && cell(t, i, 'case_name') === cs);
        return r < 0 ? null : Object.assign(item(ctx, t, r, 'exposure'), { s: si });
      }).filter(Boolean),
    }));
    ctx.legend = series.map((s) => ({ kind: 'fill', cls: s.cls, label: s.label }));
    return { engine: engineColumns, sp: { orient: 'v', mode: 'group', series, panels: [{ cats }], unit: 'US$ m' } };
  };
  BUILD['chart.headline_results'] = (ctx) => {
    const t = twinOf(ctx, 'cp1b.period_comparison');
    const series = [{ label: 'Reference period', cls: 'sr-3' }, { label: 'Current period', cls: 'sr-0' }];
    const cats = t.rows.map((r, i) => ({ label: WB.humanize(cell(t, i, 'metric_id')), items: [Object.assign(item(ctx, t, i, 'reference_value'), { s: 0 }), Object.assign(item(ctx, t, i, 'current_value'), { s: 1 })] }));
    ctx.legend = series.map((s) => ({ kind: 'fill', cls: s.cls, label: s.label }));
    return { engine: engineColumns, sp: { orient: 'h', mode: 'group', series, panels: [{ cats }], unit: 'millions' } };
  };
  BUILD['chart.recovery_by_class'] = (ctx) => {
    const t = twinOf(ctx, 'cp4c.recoveries');
    const scen = uniq(t.rows.map((r, i) => cell(t, i, 'scenario')));
    const series = [{ label: 'Allowed claim', cls: 'sr-3' }, { label: 'Recovery (allocation)', cls: 'sr-0' }];
    const panels = scen.map((sc) => ({
      title: sc,
      cats: t.rows.map((r, i) => i).filter((i) => cell(t, i, 'scenario') === sc).map((i) => {
        const claim = Object.assign(item(ctx, t, i, 'allowed_claim'), { s: 0 });
        const alloc = Object.assign(item(ctx, t, i, 'allocation'), { s: 1, extra: 'recovery ' + cell(t, i, 'recovery_pct') });
        // the recovery % sits under the class name for every class (a label above a narrow bar could not always fit)
        return { label: WB.claimName(cell(t, i, 'class_id')), sub: cell(t, i, 'recovery_pct'), items: [claim, alloc] };
      }),
    }));
    ctx.legend = series.map((s) => ({ kind: 'fill', cls: s.cls, label: s.label })).concat([{ kind: 'text', label: 'Under each class name: its recovery %' }]);
    return { engine: engineColumns, sp: { orient: 'v', mode: 'group', series, panels, unit: 'US$ m', minPanelW: 280, plotH: 120 } };
  };
  BUILD['chart.factor_scores'] = (ctx) => {
    const t = twinOf(ctx, 'cp4.protection_score');
    const series = [{ label: 'Score', cls: 'sr-0' }];
    const cats = t.rows.map((r, i) => ({ label: cell(t, i, 'area'), items: [Object.assign(item(ctx, t, i, 'score'), { s: 0 })] }));
    ctx.legend = [{ kind: 'fill', cls: 'sr-0', label: 'Score, 1 to 5 (5 protects creditors most)' }];
    // the protection score is a five-point scale: the axis runs to 5 whatever the highest score
    return { engine: engineColumns, sp: { orient: 'h', mode: 'group', series, panels: [{ cats }], unit: '', max: 5, integer: true } };
  };
  BUILD['chart.implied_pd'] = (ctx) => {
    const t = twinOf(ctx, 'cp3d.implied_risk');
    const series = [{ label: 'Implied default probability', cls: 'sr-0' }];
    const cats = t.rows.map((r, i) => ({ label: String(cell(t, i, 'security_id')).replace(/\s*\(CUSIP[^)]*\)/, ''), items: [Object.assign(item(ctx, t, i, 'implied_pd_pct'), { s: 0 })] }));
    ctx.legend = [{ kind: 'fill', cls: 'sr-0', label: 'Implied default probability' }];
    return { engine: engineColumns, sp: { orient: 'h', mode: 'group', series, panels: [{ cats }], unit: '%' } };
  };

  /* waterfalls */
  function wfStep(ctx, t, r, col, kind, label, extra) {
    const it = item(ctx, t, r, col);
    return Object.assign(it, { kind, label, name: label }, extra || {});
  }
  BUILD['chart.ebitda_bridge'] = (ctx) => {
    const t = twinOf(ctx, 'snapshot.ebitda_adjustments');
    const steps = t.rows.map((r, i) => {
      const kind = cell(t, i, 'kind') === 'Total' ? 'total' : 'delta';
      const st = cell(t, i, 'realization_status');
      const extra = st === 'UNREALIZED' ? { cls: 'sr-6', dashed: true, extra: 'unrealized' } : st === 'REALIZED' ? { extra: 'realized' } : {};
      return wfStep(ctx, t, i, 'amount', kind, cell(t, i, 'line'), extra);
    });
    if (steps.some((x) => x.dashed)) ctx.seen.unreal = true;
    ctx.legend = [{ kind: 'fill', cls: 'sr-2', label: 'Stated total' }, { kind: 'fill', cls: 'sr-0', label: 'Realized add-back' }, { kind: 'fill', cls: 'sr-6 dashed', label: 'Unrealized (removed)', need: 'unreal' }, { kind: 'fill', cls: 'sg-neg', label: 'Unexplained residual', need: 'residual' }];
    return { engine: engineWaterfall, sp: { panels: [{ steps }], unit: 'US$ m' } };
  };
  BUILD['chart.liquidity_bridge'] = (ctx) => {
    const t = twinOf(ctx, 'cp2d.bridge');
    const steps = t.rows.map((r, i) => wfStep(ctx, t, i, 'amount', /total/i.test(cell(t, i, 'kind')) ? 'total' : 'delta', cell(t, i, 'step')));
    ctx.legend = [{ kind: 'fill', cls: 'sr-2', label: 'Opening and closing liquidity' }, { kind: 'fill', cls: 'sr-0', label: 'Inflow' }, { kind: 'fill', cls: 'sr-1', label: 'Use' }, { kind: 'fill', cls: 'sg-neg', label: 'Unexplained residual', need: 'residual' }];
    return { engine: engineWaterfall, sp: { panels: [{ steps }], unit: 'US$ m' } };
  };
  BUILD['chart.adjusted_debt_bridge'] = (ctx) => {
    const t = twinOf(ctx, 'cp1d.debt_like_items');
    const house = WB.run.model && WB.run.model.house && WB.run.model.house.adjusted_debt;
    if (!house || house.value == null) throw new Error('chart.adjusted_debt_bridge: the Model carries no adjusted debt');
    const line = WB.modelLine('total_debt');
    const mc = line && WB.modelCell('total_debt', house.column_id);
    if (!mc || mc.value == null) throw new Error('chart.adjusted_debt_bridge: no total debt in column ' + house.column_id);
    const steps = [{ kind: 'total', label: 'Total debt', v: num(mc.value), raw: String(mc.value), k: 'solid', word: 'calculated', desc: { t: 'mcell', lineId: 'total_debt', columnId: house.column_id }, name: 'Total debt' }];
    t.rows.forEach((r, i) => steps.push(wfStep(ctx, t, i, 'amount', 'delta', cell(t, i, 'item'))));
    steps.push({ kind: 'total', label: 'Adjusted debt', v: num(house.value), raw: String(house.value), k: 'solid', word: 'calculated', name: 'Adjusted debt', desc: { t: 'note', kind: 'calculated', code: 'model.house', title: 'Adjusted debt', sub: 'Model house view', fields: [['Served as', String(house.value), true], ['Formula', house.formula || '', true]], note: 'Computed by the host script from total debt and the debt-like items. It is the stated total this bridge is checked against.' } });
    ctx.legend = [{ kind: 'fill', cls: 'sr-2', label: 'Stated totals' }, { kind: 'fill', cls: 'sr-0', label: 'Debt-like item' }, { kind: 'fill', cls: 'sg-neg', label: 'Unexplained residual', need: 'residual' }];
    return { engine: engineWaterfall, sp: { panels: [{ steps }], unit: 'US$ m' } };
  };
  BUILD['chart.value_allocation'] = (ctx) => {
    const t = twinOf(ctx, 'cp4c.recoveries');
    const scen = uniq(t.rows.map((r, i) => cell(t, i, 'scenario')));
    const panels = scen.map((sc) => {
      const rows = t.rows.map((r, i) => i).filter((i) => cell(t, i, 'scenario') === sc);
      const steps = [wfStep(ctx, t, rows[0], 'available_value', 'total', 'Available value')];
      rows.forEach((i) => {
        const a = item(ctx, t, i, 'allocation');
        // each class by name (the claims register's words); the allocation as served, grouped
        steps.push(Object.assign(a, { kind: 'delta', label: WB.claimName(cell(t, i, 'class_id')), v: isNaN(a.v) ? a.v : -a.v, fulcrum: cell(t, i, 'fulcrum') === 'Yes', txt: lab(a.raw), extra: cell(t, i, 'fulcrum') === 'Yes' ? 'fulcrum' : '' }));
      });
      const last = rows[rows.length - 1];
      steps.push(wfStep(ctx, t, last, 'residual', 'total', 'Residual'));
      return { title: String(sc).replace(/: /, ', '), steps };
    });
    ctx.legend = [{ kind: 'fill', cls: 'sr-2', label: 'Available value, residual' }, { kind: 'fill', cls: 'sr-1', label: 'Allocated to a class' }, { kind: 'ring', label: 'Fulcrum class' }, { kind: 'fill', cls: 'sg-neg', label: 'Unexplained residual', need: 'residual' }];
    return { engine: engineWaterfall, sp: { panels, unit: 'US$ m', minPanelW: 340 } };
  };

  /* bullets */
  function toneOf(head, thr, breach) {
    if (breach || head < 0) return { tone: 'neg', word: 'Breached' };
    if (Math.abs(thr) > 0 && head / Math.abs(thr) < 0.1) return { tone: 'cau', word: 'Tight' };
    return { tone: 'pos', word: 'Headroom' };
  }
  function covenantRows(ctx, t, o) {
    return t.rows.map((r, i) => {
      const dir = cell(t, i, 'direction');
      const curI = item(ctx, t, i, 'current_value');
      const thrI = item(ctx, t, i, 'threshold');
      const headI = item(ctx, t, i, 'headroom');
      const unit = unitText(cell(t, i, 'unit_label'));
      let head = headI.v;
      if (isNaN(head) && !isNaN(curI.v) && !isNaN(thrI.v)) head = dir === 'Floor' ? curI.v - thrI.v : thrI.v - curI.v;
      const breachNow = !isNaN(curI.v) && !isNaN(thrI.v) && (dir === 'Floor' ? curI.v < thrI.v : curI.v > thrI.v);
      const tn = toneOf(head, thrI.v, breachNow);
      const headNum = headI.k === 'gap' ? '' : tn.tone === 'neg' ? '(' + String(headI.raw).replace(/^[-−(]|\)$/g, '') + ')' : lab(headI.raw);
      const row = { label: o.label(i), sub: o.sub ? o.sub(i, dir) : dir === 'Floor' ? 'Floor' : 'Ceiling', group: unit || 'x', groupLabel: unit, unit, cur: curI.v, thr: thrI.v, dir, curI, thrI, headI, tone: tn.tone, word: tn.word, headText: withUnitTight(headNum, unit) };
      if (o.proj) {
        const pI = item(ctx, t, i, 'projected_value');
        row.projI = pI;
        row.proj = pI.v;
        row.projBreach = !isNaN(pI.v) && !isNaN(thrI.v) && (dir === 'Floor' ? pI.v < thrI.v : pI.v > thrI.v);
      }
      return row;
    });
  }
  BUILD['chart.covenant_headroom'] = (ctx) => {
    const t = twinOf(ctx, 'cp4.covenant_tests');
    const rows = covenantRows(ctx, t, { label: (i) => cell(t, i, 'test') });
    ctx.legend = [{ kind: 'fill', cls: 'sr-0', label: 'Current' }, { kind: 'rule', label: 'Threshold' }, { kind: 'band', tone: 'pos', label: 'Headroom' }, { kind: 'band', tone: 'cau', label: 'Tight (under 10% of threshold)' }, { kind: 'band', tone: 'neg', label: 'Breached' }];
    return { engine: engineBullets, sp: { rows, scale: 'unit' } };
  };
  BUILD['chart.rating_triggers'] = (ctx) => {
    const t = twinOf(ctx, 'cp2h.rating_triggers');
    const rows = covenantRows(ctx, t, { label: (i) => cell(t, i, 'metric'), sub: (i, dir) => cell(t, i, 'agency') + ' · ' + (dir === 'Floor' ? 'floor' : 'ceiling'), proj: true });
    ctx.legend = [{ kind: 'fill', cls: 'sr-0', label: 'Current' }, { kind: 'rule', label: 'Trigger threshold' }, { kind: 'diamond', label: 'Projected' }, { kind: 'band', tone: 'pos', label: 'Headroom' }, { kind: 'band', tone: 'neg', label: 'Breached' }];
    return { engine: engineBullets, sp: { rows, scale: 'unit' } };
  };
  BUILD['chart.fit_bullets'] = (ctx) => {
    const t = twinOf(ctx, 'fit.limit_headroom');
    const groups = new Map();
    t.rows.forEach((r, i) => {
      const key = r.join('\u0001');
      if (!groups.has(key)) groups.set(key, { first: i, n: 0 });
      groups.get(key).n++;
    });
    let list = Array.from(groups.values());
    const limitN = ctx.opts.limit || 14;
    let limited = '';
    const rowsAll = list.map((g) => {
      const i = g.first;
      const parameter = cell(t, i, 'parameter');
      const dir = 'Limit';
      const limI = item(ctx, t, i, 'limit_value');
      const curI = item(ctx, t, i, 'current_value', { lenient: true });
      const headI = item(ctx, t, i, 'headroom', { lenient: true });
      const lu = cell(t, i, 'limit_unit');
      const unit = lu === 'pct_nav' ? '% NAV' : lu === 'pct' ? '%' : '';
      const head = headI.v;
      const tn = toneOf(isNaN(head) ? 1 : head, limI.v, false);
      return { label: parameter.replace(/^(Max|Min)\s+/i, (m) => cap1(m.trim()) + ' '), sub: cell(t, i, 'limit_kind') + ' limit' + (g.n > 1 ? ' · ' + g.n + ' identical rows in the table' : ''), group: 'row', unit, cur: curI.v, thr: limI.v, dir, curI, thrI: limI, headI, tone: tn.tone, word: tn.word, headText: String(headI.raw), ratio: isNaN(head) || !limI.v ? 1 : head / Math.abs(limI.v) };
    });
    let rows = rowsAll;
    if (rows.length > limitN) {
      rows = rowsAll.slice().sort((a, b) => a.ratio - b.ratio).slice(0, limitN);
      limited = 'Showing the ' + limitN + ' tightest of ' + rowsAll.length + ' limits; the Table lists all.';
    }
    ctx.legend = [{ kind: 'fill', cls: 'sr-0', label: 'Current' }, { kind: 'rule', label: 'Limit' }, { kind: 'band', tone: 'pos', label: 'Headroom' }, { kind: 'band', tone: 'cau', label: 'Tight' }, { kind: 'band', tone: 'neg', label: 'Breached' }];
    return { engine: engineBullets, sp: { rows, scale: 'row', limited } };
  };

  /* dumbbells */
  BUILD['chart.kpi_changes'] = (ctx) => {
    const t = twinOf(ctx, 'cp1b.kpi_changes');
    const rows = t.rows.map((r, i) => ({ label: cell(t, i, 'kpi_id'), a: item(ctx, t, i, 'reference_value'), b: item(ctx, t, i, 'current_value'), aName: 'Reference', bName: 'Current', unit: '%', issuer: true, aHollow: true }));
    ctx.legend = [{ kind: 'ring', label: 'Reference period' }, { kind: 'dotf', cls: 'sr-0', label: 'Current period' }];
    return { engine: engineDumbbell, sp: { rows, shared: true, unit: '% (margins)' } };
  };
  BUILD['chart.what_changed'] = (ctx) => {
    const t = twinOf(ctx, 'prior/diff.json');
    const rows = t.rows.map((r, i) => ({ label: cap0(WB.humanize(String(cell(t, i, 'key')).replace(/^metric:/, ''))), sub: WB.tableTitle(String(cell(t, i, 'table'))) + ' · ' + WB.colLabel(String(cell(t, i, 'field'))), a: item(ctx, t, i, 'prior'), b: item(ctx, t, i, 'current'), aName: 'Prior Case', bName: 'Current', issuer: true, aHollow: true }));
    ctx.legend = [{ kind: 'ring', label: 'Prior Case' }, { kind: 'dotf', cls: 'sr-0', label: 'Current' }, { kind: 'text', label: 'Each row has its own scale' }];
    return { engine: engineDumbbell, sp: { rows, shared: false } };
  };
  BUILD['chart.expected_realised'] = (ctx) => {
    const t = twinOf(ctx, 'cp8.thesis_review');
    const rows = t.rows.map((r, i) => {
      const a = item(ctx, t, i, 'expected');
      const b = item(ctx, t, i, 'realised');
      const base = { label: cell(t, i, 'prior_item'), aName: 'Expected', bName: 'Realised', issuer: true, aHollow: true };
      if (isNaN(a.v) || isNaN(b.v)) {
        const shown = 'Expected: ' + a.raw + '  ·  Realised: ' + b.raw;
        return Object.assign(base, { issuer: false, text: { shown: shown.length > 90 ? shown.slice(0, 88) + '…' : shown, label: nm(base.label, 'expected ' + a.raw, 'realised ' + b.raw, 'no figure to plot on both sides'), desc: { t: 'row', table: t.id, r: i } } });
      }
      return Object.assign(base, { a, b });
    });
    ctx.legend = [{ kind: 'ring', label: 'Expected' }, { kind: 'dotf', cls: 'sr-0', label: 'Realised' }, { kind: 'text', label: 'Each row has its own scale; rows without two figures show their words' }];
    return { engine: engineDumbbell, sp: { rows, shared: false } };
  };
  function rvBuild(ctx, block) {
    const t = twinOf(ctx, 'snapshot.relative_value');
    const idx = [];
    const comps = [];
    t.rows.forEach((r, i) => (/index/i.test(cell(t, i, 'block')) ? idx : comps).push(i));
    const bucket = (rt) => String(rt).split('/').pop().trim().replace(/[+\-]$/, '').toUpperCase();
    const rows = comps.map((i) => {
      const rt = cell(t, i, 'ratings');
      const bk = bucket(rt);
      const ix = idx.find((j) => bucket(cell(t, j, 'ratings')) === bk);
      const issuer = isIssuer(ctx, cell(t, i, 'name'));
      const b = Object.assign(item(ctx, t, i, 'yield_pct'), {});
      const a = ix == null ? null : item(ctx, t, ix, 'yield_pct');
      const bps = cell(t, i, 'spread_or_dm_bps');
      return { label: cell(t, i, 'name').replace(/\s*\(synthetic\)/, ''), sub: rt + (ix == null ? ' · no index in its rating bucket' : ''), a, b, aName: ix == null ? 'Index' : cell(t, ix, 'name'), bName: 'Yield', issuer, aSquare: true, right: WB.isEmpty(bps) ? '' : bps + ' bps', unit: '', bCls: 'sr-1' };
    });
    const idxOnly = idx.filter((j) => !rows.some((r) => r.a && r.a.r === j));
    ctx.legend = [{ kind: 'square', cls: 'sr-3', label: 'Index of its rating bucket' }, { kind: 'dotf', cls: 'sr-0', label: 'Issuer security' }, { kind: 'dotf', cls: 'sr-1', label: 'Comparable' }, { kind: 'text', label: 'Right: spread or discount margin' }];
    if (idxOnly.length) ctx.notes.push('Index rows with no comparable in their rating bucket: ' + idxOnly.map((j) => cell(t, j, 'name') + ' ' + cell(t, j, 'yield_pct')).join('; ') + '.');
    return { engine: engineDumbbell, sp: { rows, shared: true, unit: 'yield %' } };
  }
  BUILD['chart.rv_loan'] = (ctx) => rvBuild(ctx);
  BUILD['chart.rv_hy'] = (ctx) => rvBuild(ctx);

  /* range strips */
  BUILD['chart.talk_range'] = (ctx) => {
    const t = twinOf(ctx, 'cp3.talk_valuation');
    const rows = t.rows.map((r, i) => ({
      label: cell(t, i, 'facility_id'),
      style: 'range',
      rangeName: 'Implied range',
      dotCls: 'sr-1',
      items: [
        Object.assign(item(ctx, t, i, 'implied_low'), { role: 'low', nameS: 'Implied low' }),
        Object.assign(item(ctx, t, i, 'implied_mid'), { role: 'mid', nameS: 'Implied mid' }),
        Object.assign(item(ctx, t, i, 'implied_high'), { role: 'high', nameS: 'Implied high' }),
        Object.assign(item(ctx, t, i, 'comparable_level'), { role: 'dot', nameS: 'Comparable level' }),
      ],
    }));
    ctx.legend = [{ kind: 'fill', cls: 'sr-6', label: 'Implied low to high' }, { kind: 'rule', label: 'Mid' }, { kind: 'dotf', cls: 'sr-1', label: 'Comparable level' }, { kind: 'text', label: 'Each tranche has its own scale' }];
    return { engine: engineRange, sp: { rows, shared: false } };
  };
  BUILD['chart.peer_ranges'] = (ctx) => {
    const t = twinOf(ctx, 'cp1c.positioning');
    const roles = [['min', 'peer_min', 'Peer minimum'], ['q1', 'peer_q1', 'Peer first quartile'], ['median', 'peer_median', 'Peer median'], ['q3', 'peer_q3', 'Peer third quartile'], ['max', 'peer_max', 'Peer maximum']];
    const rows = t.rows.map((r, i) => ({
      label: WB.humanize(cell(t, i, 'metric_id')),
      sub: 'Peers in ' + cell(t, i, 'unit_label'),
      style: 'peer',
      rangeName: 'Peer range',
      dotCls: 'sr-0',
      items: roles.map(([role, col, nameS]) => Object.assign(item(ctx, t, i, col), { role, nameS })).concat([Object.assign(item(ctx, t, i, 'borrower_value'), { role: 'dot', nameS: 'Borrower' })]),
    }));
    ctx.legend = [{ kind: 'fill', cls: 'sr-6', label: 'First to third quartile' }, { kind: 'rule', label: 'Median' }, { kind: 'dotf', cls: 'sr-0', label: 'Borrower' }, { kind: 'text', label: 'Whiskers: peer minimum and maximum' }];
    return { engine: engineRange, sp: { rows, shared: false } };
  };
  BUILD['chart.implied_ev'] = (ctx) => {
    const t = twinOf(ctx, 'cp1c.valuation_multiples');
    const rows = t.rows.map((r, i) => ({
      label: cell(t, i, 'entity').replace(/\s*\(synthetic\)/, ''),
      sub: cell(t, i, 'basis') + (/synthetic/.test(cell(t, i, 'entity')) ? ' · synthetic' : ''),
      style: 'range',
      rangeName: 'Implied EV range',
      dotCls: 'sr-0',
      items: [
        Object.assign(item(ctx, t, i, 'implied_ev_low'), { role: 'low', nameS: 'Implied EV low' }),
        Object.assign(item(ctx, t, i, 'implied_ev_median'), { role: 'mid', nameS: 'Implied EV median' }),
        Object.assign(item(ctx, t, i, 'implied_ev_high'), { role: 'high', nameS: 'Implied EV high' }),
        Object.assign(item(ctx, t, i, 'ev'), { role: 'dot', nameS: 'Enterprise value' }),
      ],
    }));
    ctx.legend = [{ kind: 'fill', cls: 'sr-6', label: 'Implied EV, low to high' }, { kind: 'rule', label: 'Median' }, { kind: 'dotf', cls: 'sr-0', label: 'Enterprise value' }];
    return { engine: engineRange, sp: { rows, shared: true, unit: 'US$ m' } };
  };

  /* tornado */
  BUILD['chart.rate_fx_tornado'] = (ctx) => {
    const t = twinOf(ctx, 'cp2e.sensitivities');
    const rows = t.rows.map((r, i) => ({ label: cell(t, i, 'sensitivity'), i: item(ctx, t, i, 'cash_impact') }));
    ctx.legend = [{ kind: 'fill', cls: 'sr-1', label: 'Adverse (cash falls)' }, { kind: 'fill', cls: 'sr-0', label: 'Favourable' }];
    return { engine: engineTornado, sp: { rows, unit: 'US$ m cash impact' } };
  };
  BUILD['chart.downside_tornado'] = (ctx) => {
    const t = twinOf(ctx, 'cp2a.sensitivities');
    const rows = t.rows.map((r, i) => ({ label: cell(t, i, 'sensitivity'), sub: unitText(cell(t, i, 'unit_label')), i: item(ctx, t, i, 'result') }));
    ctx.legend = [{ kind: 'fill', cls: 'sr-1', label: 'Adverse' }, { kind: 'fill', cls: 'sr-0', label: 'Favourable' }, { kind: 'text', label: 'Measure under each name' }];
    return { engine: engineTornado, sp: { rows, unit: 'US$ m' } };
  };

  /* risk matrix */
  BUILD['chart.risk_matrix'] = (ctx) => {
    const t = twinOf(ctx, 'cp2a.downside_paths');
    const lv = ['Low', 'Medium', 'High'];
    const hasUnknown = t.rows.some((r, i) => cell(t, i, 'probability') === 'Unknown' || cell(t, i, 'impact') === 'Unknown');
    const cols = lv.slice().concat(hasUnknown ? ['Unknown'] : []);
    const rowsL = lv.slice().reverse().concat(hasUnknown ? ['Unknown'] : []);
    const cells = [];
    t.rows.forEach((r, i) => {
      const p = cell(t, i, 'probability');
      const im = cell(t, i, 'impact');
      const ci = cols.indexOf(p);
      const ri = rowsL.indexOf(im);
      if (ci < 0 || ri < 0) throw new Error('chart.risk_matrix: unknown level ' + p + ' / ' + im);
      let c = cells.find((x) => x.c === ci && x.r === ri);
      if (!c) cells.push((c = { c: ci, r: ri, chips: [] }));
      const o = og(ctx, t, i, 'probability');
      c.chips.push({ raw: cell(t, i, 'path_id'), prob: p, impact: im, k: o.k === 'gap' ? 'soft' : o.k, word: o.word, desc: { t: 'row', table: t.id, r: i } });
    });
    ctx.legend = [{ kind: 'text', label: 'Each chip is one downside path; darker cells combine higher probability and impact' }];
    return { engine: engineMatrix, sp: { cols, rows: rowsL, cells } };
  };

  /* spread curve */
  BUILD['chart.spread_curve'] = (ctx) => {
    const t = twinOf(ctx, 'cp3d.observations');
    const sen = uniq(t.rows.map((r, i) => cell(t, i, 'seniority')));
    const series = sen.map((s, i) => ({ label: s, cls: 'sr-' + [0, 1, 2, 3, 4][i % 5] }));
    const points = t.rows.map((r, i) => {
      const it = item(ctx, t, i, 'spread_or_dm_bps');
      const dateRaw = cell(t, i, 'maturity_or_call_date');
      const name = cell(t, i, 'security_id');
      return Object.assign(it, { s: sen.indexOf(cell(t, i, 'seniority')), x: Date.parse(dateRaw), xText: WB.fmtDate ? WB.fmtDate(dateRaw) : dateRaw, name, short: name.replace(/\s*\(.*$/, '').replace(/,.*$/, ''), issuer: isIssuer(ctx, name) });
    });
    ctx.legend = series.map((s, i) => ({ kind: 'point', shape: SHAPES[i % SHAPES.length], cls: s.cls, label: s.label })).concat([{ kind: 'text', label: 'Filled: issuer security; hollow: other' }]);
    return { engine: engineScatter, sp: { points, series } };
  };

  /* capital structure */
  BUILD['chart.capital_structure'] = (ctx) => {
    const t = twinOf(ctx, 'snapshot.capital_structure');
    const tot = twinOf(ctx, 'snapshot.capital_structure_totals');
    const ranks = uniq(t.rows.map((r, i) => cell(t, i, 'rank')));
    const series = rankSeries(ranks);
    const rows = t.rows.map((r, i) => ({ label: cell(t, i, 'facility'), rank: cell(t, i, 'rank'), cls: series[ranks.indexOf(cell(t, i, 'rank'))].cls, i: item(ctx, t, i, 'outstanding') }));
    const find = (re) => tot.rows.findIndex((r, i) => re.test(cell(tot, i, 'line')));
    const mk = (re, name, dash) => {
      const r = find(re);
      if (r < 0) return null;
      const i = item(ctx, tot, r, 'amount');
      const m = String(cell(tot, r, 'structuring_multiple_x'));
      return { name, i, mult: WB.isEmpty(m) ? '' : m, dash };
    };
    const sec = mk(/^senior secured/i, 'Secured');
    const totR = mk(/^total debt/i, 'Total debt');
    const ev = mk(/^ev$/i, 'EV', true);
    const rules = [sec, totR, ev].filter(Boolean);
    const tm = totR ? num(totR.mult) : NaN;
    const perX = totR && !isNaN(totR.i.v) && !isNaN(tm) && tm > 0 ? totR.i.v / tm : 0;
    const cum = rows.reduce((a, r) => a + (isNaN(r.i.v) ? 0 : r.i.v), 0);
    ctx.legend = series.map((s) => ({ kind: 'fill', cls: s.cls, label: s.label })).concat([{ kind: 'rule', label: 'Secured, total and EV markers (Structuring multiple)' }]);
    return { engine: engineStack, sp: { rows, rules, perX, total: totR && totR.i.v, ev: ev && ev.i.v, cum } };
  };

  /* model strip, forecast and credit path */
  function projYears(tw) {
    return uniq(tw.rows.map((r, i) => String(cell(tw, i, 'fiscal_year'))));
  }
  function buildLines(ctx, cfg) {
    // cfg.hist: [{col, full, short}] (may be empty); cfg.panels: [{title, unit, hist:{t,r}|null, proj:{t,col}|null, histNote}]
    const pj = cfg.projTable;
    const years = pj ? projYears(pj) : [];
    const cats = cfg.hist.map((h) => ({ full: h.full, short: h.short })).concat(years.map((y) => ({ full: 'FY' + y + 'E, projected', short: y.slice(2) + 'E' })));
    const nH = cfg.hist.length;
    const panels = cfg.panels.map((p) => {
      const series = [];
      let lastHist = null;
      if (p.hist) {
        const pts = cfg.hist.map((h, i) => {
          if (p.hist.t.columns.indexOf(h.col) < 0) throw new Error('chart column missing: ' + p.hist.t.id + '.' + h.col);
          const it = item(ctx, p.hist.t, p.hist.r, h.col, { lenient: false });
          it.i = i;
          return it;
        });
        series.push({ label: cfg.histLabel || 'Reported', cls: 'sr-0', proj: false, pts });
        lastHist = pts.filter((q) => !isNaN(q.v)).pop() || null;
      }
      if (p.proj && pj) {
        const cases = uniq(pj.rows.map((r, i) => String(cell(pj, i, 'case'))));
        cases.forEach((cs, ci) => {
          const pts = [];
          years.forEach((y, yi) => {
            const r = pj.rows.findIndex((_, i) => cell(pj, i, 'case') === cs && String(cell(pj, i, 'fiscal_year')) === y);
            if (r < 0) return;
            const it = item(ctx, pj, r, p.proj);
            it.i = nH + yi;
            pts.push(it);
          });
          series.push({ label: cap1(cs) + ' (projected)', cls: cs === 'DOWNSIDE' ? 'sr-1' : 'sr-0', proj: true, pts, from: nH && lastHist ? { i: lastHist.i, v: lastHist.v } : null });
        });
      }
      return { title: p.title, unit: p.unit, series };
    });
    const names = [];
    panels.forEach((p) => p.series.forEach((s) => !names.some((n) => n.label === s.label) && names.push({ label: s.label, cls: s.cls, proj: s.proj })));
    ctx.legend = names.map((n) => ({ kind: n.proj ? 'dash' : 'line', cls: n.cls, label: n.label }));
    return { engine: engineLines, sp: { cats, panels, divider: years.length && nH ? nH : null, minPanelW: cfg.minPanelW } };
  }
  function histCols(wide) {
    const cols = (WB.run.model && WB.run.model.columns) || [];
    const fy = cols.filter((c) => c.kind === 'FY');
    const out = [];
    const at = (k) => fy[fy.length - 1 - k];
    [['fy_2', 2], ['fy_1', 1], ['fy', 0]].forEach(([col, k]) => {
      const c = at(k);
      if (c) out.push({ col, full: c.label, short: String(c.label).replace(/^FY20/, 'FY') });
    });
    if (wide) {
      const ltm = cols.find((c) => c.kind === 'LTM');
      const pf = cols.find((c) => c.kind === 'PF_LTM');
      if (ltm) out.push({ col: 'ltm', full: ltm.label, short: 'LTM' });
      if (pf) out.push({ col: 'pf_ltm', full: pf.label, short: 'PF' });
    }
    return out;
  }
  BUILD['chart.model_strip'] = (ctx) => {
    const mt = twinOf(ctx, 'model.metrics');
    const ms = twinOf(ctx, 'model.summary');
    const pj = optTwin(ctx, 'model.projection_summary');
    const rowOf = (t, col, id) => t.rows.findIndex((_, i) => cell(t, i, col) === id);
    const panels = [];
    const lev = rowOf(mt, 'metric_id', 'net_leverage_adjusted');
    const cov = rowOf(mt, 'metric_id', 'interest_coverage_adjusted');
    const liq = rowOf(ms, 'line_id', 'liquidity');
    if (lev >= 0) panels.push({ title: 'Net leverage', unit: 'x', hist: { t: mt, r: lev }, proj: pj && pj.columns.includes('net_leverage_adjusted_x') ? 'net_leverage_adjusted_x' : null });
    if (cov >= 0) panels.push({ title: 'Interest cover', unit: 'x', hist: { t: mt, r: cov }, proj: pj && pj.columns.includes('interest_coverage_adjusted_x') ? 'interest_coverage_adjusted_x' : null });
    if (liq >= 0) panels.push({ title: 'Liquidity', unit: unitText(cell(ms, liq, 'unit_label')), hist: { t: ms, r: liq }, proj: pj && pj.columns.includes('liquidity') ? 'liquidity' : null });
    if (!panels.length) throw new Error('chart.model_strip: none of its metrics is in the data');
    return buildLines(ctx, { hist: histCols(true), histLabel: 'Reported', panels, projTable: pj && panels.some((p) => p.proj) ? pj : null, minPanelW: 230 });
  };
  BUILD['chart.forecast_lines'] = (ctx) => {
    const ms = twinOf(ctx, 'model.summary');
    const pj = twinOf(ctx, 'model.projection_summary');
    const panels = ms.rows.map((r, i) => ({ title: String(cell(ms, i, 'label')).replace(/\s*\(SSIM basis\)/, ''), unit: unitText(cell(ms, i, 'unit_label')), hist: { t: ms, r: i }, proj: pj.columns.includes(cell(ms, i, 'line_id')) ? cell(ms, i, 'line_id') : null }));
    return buildLines(ctx, { hist: histCols(false), histLabel: 'Reported', panels, projTable: pj, minPanelW: 230 });
  };
  BUILD['chart.credit_path'] = (ctx) => {
    const pj = twinOf(ctx, 'model.projection_summary');
    const defs = [['net_leverage_adjusted_x', 'Net leverage', 'x'], ['interest_coverage_adjusted_x', 'Interest cover', 'x'], ['fcf_to_debt_pct', 'FCF to debt', '%']];
    const panels = defs.filter((d) => pj.columns.includes(d[0])).map((d) => ({ title: d[1], unit: d[2], hist: null, proj: d[0] }));
    return buildLines(ctx, { hist: [], panels, projTable: pj, minPanelW: 230 });
  };

  /* ---------- legend, frame, redraw ---------- */
  function swatch(e, uid) {
    const svg = S('svg', { width: 22, height: 12, viewBox: '0 0 22 12', 'aria-hidden': 'true', class: 'lg-sw' });
    const cls = e.cls || 'sr-3';
    switch (e.kind) {
      case 'line': svg.appendChild(S('line', { x1: 1, x2: 21, y1: 6, y2: 6, class: 'ln ' + cls })); svg.appendChild(S('circle', { cx: 11, cy: 6, r: 3, class: 'sh ' + cls })); break;
      case 'dash': svg.appendChild(S('line', { x1: 1, x2: 21, y1: 6, y2: 6, class: 'ln proj ' + cls })); svg.appendChild(S('circle', { cx: 11, cy: 6, r: 3, class: 'ring ' + cls })); break;
      case 'ring': svg.appendChild(S('circle', { cx: 11, cy: 6, r: 4, class: 'ring sr-3' + (e.label === 'Fulcrum class' ? ' fulcrum-ring' : '') })); break;
      case 'dotf': svg.appendChild(S('circle', { cx: 11, cy: 6, r: 4, class: 'sh ' + cls })); break;
      case 'square': svg.appendChild(S('rect', { x: 7, y: 2, width: 8, height: 8, class: 'sh ' + cls })); break;
      case 'diamond': svg.appendChild(S('path', { d: 'M11 1L16 6L11 11L6 6Z', class: 'proj-dot' })); break;
      case 'rule': svg.appendChild(S('line', { x1: 11, x2: 11, y1: 0, y2: 12, class: 'rule-mk' })); break;
      case 'band': svg.appendChild(S('rect', { x: 2, y: 2, width: 18, height: 8, class: 'band tn-' + e.tone + '-f' })); break;
      case 'point': svg.appendChild(pointShape({ seen: {} }, e.shape, 11, 6, 3.6, cls, 'solid', true)); break;
      case 'na': svg.appendChild(S('text', { x: 11, y: 9.5, class: 'na', 'text-anchor': 'middle', text: 'n/a' })); break;
      case 'hatch': {
        const defs = S('defs');
        hatchIn(defs, 'lg' + uid, cls);
        svg.appendChild(defs);
        svg.appendChild(S('rect', { x: 2, y: 1, width: 18, height: 10, class: 'sh ' + cls + ' o-soft', style: 'fill:url(#lg' + uid + ')' }));
        break;
      }
      default: svg.appendChild(S('rect', { x: 2, y: 1, width: 18, height: 10, class: 'sh ' + cls }));
    }
    return svg;
  }
  function legendEl(ctx) {
    // an entry tied to a state (an unexplained residual, an unrealized add-back) shows only when the chart draws one
    const items = (ctx.legend || []).filter((e) => e.kind !== 'text' && (!e.need || ctx.seen[e.need]));
    const notes = (ctx.legend || []).filter((e) => e.kind === 'text');
    const prov = [];
    if (ctx.seen.syn) prov.push({ kind: 'fill', cls: 'sr-3 o-syn', label: 'Synthetic: slate outline' });
    if (ctx.seen.soft) prov.push({ kind: 'hatch', cls: 'sr-3', label: 'Model-written or illustrative: hatched or dashed' });
    if (ctx.seen.proj && !items.some((e) => e.kind === 'dash')) prov.push({ kind: 'dash', cls: 'sr-3', label: 'Projected: dashed' });
    if (ctx.seen.gap) prov.push({ kind: 'na', label: 'Not available; the gap id sits on the axis' });
    const all = items.concat(prov);
    return el('ul', { class: 'wbc-legend', 'aria-label': 'Legend' }, all.map((e) => el('li', null, [swatch(e, ++UID), e.label])).concat(notes.map((n) => el('li', { class: 'lg-note' }, n.label))));
  }

  function roving(ctx, svg, keepIdx) {
    const marks = ctx.marks;
    marks.forEach((m, i) => m.setAttribute('tabindex', i === (keepIdx != null && keepIdx < marks.length ? keepIdx : 0) ? '0' : '-1'));
    svg.addEventListener('keydown', (e) => {
      const g = e.target.closest && e.target.closest('g.mk');
      if (!g) return;
      const i = marks.indexOf(g);
      let n = null;
      if (e.key === 'ArrowRight' || e.key === 'ArrowDown') n = Math.min(marks.length - 1, i + 1);
      else if (e.key === 'ArrowLeft' || e.key === 'ArrowUp') n = Math.max(0, i - 1);
      else if (e.key === 'Home') n = 0;
      else if (e.key === 'End') n = marks.length - 1;
      else if (e.key === 'Escape') hideTip(ctx);
      if (n == null) return;
      e.preventDefault();
      marks.forEach((m, k) => m.setAttribute('tabindex', k === n ? '0' : '-1'));
      marks[n].focus();
    });
    const show = (e) => {
      const g = e.target.closest && e.target.closest('g.mk');
      if (!g) return;
      marks.forEach((m) => m.setAttribute('tabindex', m === g ? '0' : '-1'));
      showTip(ctx, g);
    };
    svg.addEventListener('focusin', show);
    svg.addEventListener('mouseover', (e) => {
      const g = e.target.closest && e.target.closest('g.mk');
      if (g) showTip(ctx, g);
    });
    svg.addEventListener('mouseleave', () => hideTip(ctx));
    svg.addEventListener('focusout', () => hideTip(ctx));
  }
  function showTip(ctx, g) {
    const tip = ctx.tip;
    tip.textContent = g._tip + '. Enter opens the source.';
    tip.hidden = false;
    const pr = ctx.plot.getBoundingClientRect();
    const gr = g.getBoundingClientRect();
    const w = Math.min(300, tip.offsetWidth || 220);
    const left = Math.max(0, Math.min(gr.left - pr.left + gr.width / 2 - w / 2, pr.width - w));
    let topPos = gr.top - pr.top - (tip.offsetHeight || 36) - 6;
    if (topPos < -8) topPos = gr.bottom - pr.top + 6;
    tip.style.left = left + 'px';
    tip.style.top = topPos + 'px';
  }
  const hideTip = (ctx) => (ctx.tip.hidden = true);

  function drawInto(plot, tip, chart, twins, opts, noteHost, legendHost) {
    const had = plot.contains(document.activeElement) ? Array.from(plot.querySelectorAll('g.mk')).indexOf(document.activeElement.closest('g.mk')) : -1;
    const uid = ++UID;
    while (plot.firstChild) plot.removeChild(plot.firstChild);
    const W = Math.max(300, Math.floor(plot.clientWidth || opts.width || 640) - 1);
    const svg = S('svg', { class: 'wbc-svg', role: 'group', tabindex: '-1', focusable: 'false', 'aria-label': WB.chartTitle(chart.chart_id) + ', chart. Each mark is a button; arrow keys move between marks.' });
    const ctx = { chart, twins, opts, W, svg, plot, tip, uid, defs: S('defs'), patterns: {}, marks: [], seen: {}, notes: [], legend: [] };
    svg.appendChild(ctx.defs);
    const b = BUILD[chart.chart_id];
    if (!b) throw new Error('No chart map for ' + chart.chart_id + ' (kind ' + chart.kind + ')');
    const built = b(ctx);
    const H = built.engine(ctx, built.sp);
    svg.setAttribute('width', W);
    svg.setAttribute('height', Math.ceil(H));
    svg.setAttribute('viewBox', '0 0 ' + W + ' ' + Math.ceil(H));
    plot.appendChild(svg);
    plot.appendChild(tip);
    roving(ctx, svg, had >= 0 ? had : null);
    if (had >= 0 && ctx.marks[had]) ctx.marks[had].focus({ preventScroll: true });
    while (legendHost.firstChild) legendHost.removeChild(legendHost.firstChild);
    legendHost.appendChild(legendEl(ctx));
    while (noteHost.firstChild) noteHost.removeChild(noteHost.firstChild);
    ctx.notes.forEach((n) => noteHost.appendChild(el('p', { class: 'wbc-note' }, [WB.icon('warn', { size: 13 }), n])));
    noteHost.hidden = !ctx.notes.length;
  }

  /* WB.chart(host, chartRecord, opts): opts = { compact, limit, caption, width } */
  WB.chart = function (host, chart, opts) {
    const o = opts || {};
    const twins = WB.chartTwinTables(chart);
    const title = WB.chartTitle(chart.chart_id);
    const root = el('div', { class: 'wbc', 'data-kind': chart.kind, 'data-chart-id': chart.chart_id });
    if (o.caption) root.appendChild(el('div', { class: 'wbc-cap' }, [el('strong', null, title)]));
    if (chart.summary) root.appendChild(el('p', { class: 'wbc-sum' }, chart.summary));
    const legendHost = el('div', { class: 'wbc-lg' });
    const plot = el('div', { class: 'wbc-plot' });
    const tip = el('div', { class: 'wbc-tip', role: 'tooltip', hidden: true });
    const notes = el('div', { class: 'wbc-notes', hidden: true });
    const twinId = 'twin-' + WB.cssId(chart.chart_id) + '-' + ++UID;
    const twinBox = el('div', { class: 'wbc-twin', id: twinId, hidden: true });
    const btn = el('button', { type: 'button', class: 'wbc-toggle', 'aria-expanded': 'false', 'aria-controls': twinId }, [WB.icon('table', { size: 13 }), el('span', null, 'Table')]);
    btn.addEventListener('click', () => {
      const open = btn.getAttribute('aria-expanded') !== 'true';
      btn.setAttribute('aria-expanded', String(open));
      if (open && !twinBox.firstChild) twins.forEach((t) => twinBox.appendChild(WB.renderTable(t, { maxRows: 60, caption: title + ': ' + WB.tableTitle(t.id) })));
      twinBox.hidden = !open;
    });
    // the source in words: the tables by name and the modules that own them; the raw table ids are the tooltip
    const owners = uniq((chart.tables || []).map((t) => WB.tableOwner(t)).filter(Boolean));
    const by = owners.map((o) => (o === 'RUN_BRIEF' ? 'Run Brief' : WB.moduleName(o) + (/^CP-/.test(o) ? ' (' + o + ')' : ''))).join(', ');
    const origin = chart.origin === 'host' ? 'calculated by RBOT' : 'as the module states them';
    const src = el('p', { class: 'wbc-src', title: (chart.tables || []).join(', ') }, 'Source: ' + uniq((chart.tables || []).map((t) => WB.tableTitle(t))).join(', ') + (by ? ' (' + by + ')' : '') + '. Figures ' + origin + '; select a mark for its passport.');
    root.append(legendHost, plot, notes, el('div', { class: 'wbc-foot' }, [src, btn]), twinBox);
    host.appendChild(root);
    const redraw = () => {
      try {
        drawInto(plot, tip, chart, twins, o, notes, legendHost);
      } catch (err) {
        WB.recordError('chart', err, chart.chart_id);
        while (plot.firstChild) plot.removeChild(plot.firstChild);
        plot.appendChild(el('p', { class: 'wbc-err' }, 'This chart could not be drawn: ' + err.message + ' The table twin below has the figures.'));
        twinBox.hidden = false;
        if (!twinBox.firstChild) twins.forEach((t) => twinBox.appendChild(WB.renderTable(t, { maxRows: 60 })));
      }
    };
    redraw();
    let last = plot.clientWidth;
    if (typeof ResizeObserver === 'function') {
      let raf = 0;
      const ro = new ResizeObserver(() => {
        if (!plot.isConnected) return;
        if (Math.abs(plot.clientWidth - last) < 2) return;
        last = plot.clientWidth;
        cancelAnimationFrame(raf);
        raf = requestAnimationFrame(redraw);
      });
      ro.observe(plot);
    }
    return root;
  };

  /* One sample record per kind from the current run (record: null where the run has none), and the runs that do have it. */
  WB.chartKinds = function () {
    const kinds = ['bar', 'bullet', 'columns', 'dumbbell', 'lineStrip', 'lines', 'rangeStrip', 'riskMatrix', 'scatter', 'stackedBar', 'stackedColumns', 'tornado', 'waterfall'];
    return kinds.map((k) => {
      const rec = (WB.run.charts || []).find((c) => c.kind === k && !WB.chartUnavailable(c)) || null;
      const where = [];
      if (!rec) {
        WB.runIds.forEach((id) => {
          const r = WB.loadRun(id);
          if (r && (r.charts || []).some((c) => c.kind === k && !WB.chartUnavailable(c))) where.push(id);
        });
      }
      return { kind: k, record: rec, availableIn: where };
    });
  };
})();
