/* RBOT Report, direction C: Period spine.
   Builds the whole page from window.RBOT_DATA with RBOTUI and RBOTCharts (shared/).
   Adds one chart kind of its own, the spine track: a metric drawn against the spine's
   columns, so every track lines up with the period stops above it.
   Values print exactly as served; a missing value is an n/a gap with its reason. */
(function () {
  "use strict";
  var D = window.RBOT_DATA, UI = window.RBOTUI, C = window.RBOTCharts, el = UI.el;
  var F = D.figures, I = D.illustrative, T = D.tables;
  var SVGNS = "http://www.w3.org/2000/svg";
  var util = C.util;

  /* ================================================================ helpers */
  function $(id) { return document.getElementById(id); }
  function txt(s) { return document.createTextNode(s); }
  function clear(n) { while (n.firstChild) n.removeChild(n.firstChild); return n; }
  function frag(parts) {
    var f = document.createDocumentFragment();
    parts.forEach(function (p) { if (p === null || p === undefined || p === false) return; f.appendChild(typeof p === "string" ? txt(p) : p); });
    return f;
  }
  function sv(tag, attrs, kids) {
    var n = document.createElementNS(SVGNS, tag);
    Object.keys(attrs || {}).forEach(function (k) { var v = attrs[k]; if (v === null || v === undefined) return; if (k === "text") n.textContent = String(v); else n.setAttribute(k, String(v)); });
    (kids || []).forEach(function (k) { if (k) n.appendChild(k); });
    return n;
  }
  function cssVar(name, fallback) { return getComputedStyle(document.documentElement).getPropertyValue(name).trim() || fallback; }
  function gapId(field) { var ids = Object.keys(D.gaps); for (var i = 0; i < ids.length; i++) if (D.gaps[ids[i]].field === field) return ids[i]; return null; }
  function gapD(ref, reason) { return { v: null, prov: "gap", ref: ref || undefined, reason: reason || (ref && D.gaps[ref] ? D.gaps[ref].reason : "not in the sources") }; }
  /* a figure by its czr.json key, as a Datum */
  function fig(key) {
    var f = F[key];
    if (!f) return gapD(null, "not in the extracted figures (" + key + ")");
    var d = { v: f.v, prov: f.prov, ref: f.ref };
    if (f.reason) d.reason = f.reason;
    return d;
  }
  function withProj(d) { var o = Object.assign({}, d); o.projected = true; return o; }
  function chips(refs) { return (refs || []).map(function (r) { return UI.chip(r); }); }
  /* judgement written for the mockup: model-authored wording, its refs, the ILLUSTRATIVE tag */
  function judged(text, refs, tag) {
    return frag([el("span", { class: "prov-model", text: text })].concat(chips(refs)).concat([tag === false ? null : UI.illus()]));
  }
  function val(d, unit) { return UI.value(d, unit); }
  function td(d, unit, attrs) { var c = el("td", Object.assign({ class: "num" }, attrs || {})); UI.cell(c, d, unit); return c; }
  function tdText(d, attrs) { var c = el("td", attrs || {}); UI.cell(c, d); return c; }
  function kvRow(label, content) { return el("tr", {}, [el("th", { scope: "row", text: label }), el("td", {}, [content])]); }
  function kvTable(caption, rows, cls) {
    var t = el("table", { class: "dt dt--kv" + (cls ? " " + cls : "") });
    t.appendChild(el("caption", { class: "vh", text: caption }));
    var b = el("tbody"); rows.forEach(function (r) { if (r) b.appendChild(r); }); t.appendChild(b);
    return t;
  }
  function head(cols) {
    return el("thead", {}, [el("tr", {}, cols.map(function (c, i) {
      var p = String(c.t || c).split(" | ");
      return el("th", { scope: "col", class: c.num || (i > 0 && c.num !== false && !c.text) ? "num" : null, "data-stops": c.stops || null },
        [p[0], p[1] ? el("span", { class: "unit", text: p[1] }) : null]);
    }))]);
  }
  function bar(tag, title, meta, extra) {
    return el(tag || "h3", { class: "bar" }, [title, extra || null, meta ? el("span", { class: "bar__meta", text: meta }) : null]);
  }
  function block(id, title, meta, kids, cls, barExtra) {
    return el("section", { class: "block" + (cls ? " " + cls : ""), id: id || null, "aria-label": title }, [bar("h3", title, meta, barExtra)].concat(kids));
  }
  function illusBand(text) { return el("div", { class: "illus-band" }, [UI.illus(), el("span", { text: text })]); }
  function chartInto(kind, spec, id, extra) {
    var host = el("div", { class: "chart-host" });
    C[kind](host, Object.assign({}, spec, { id: id, headingLevel: 4 }, extra || {}));
    return host;
  }
  function dirClass(word) {
    return /improv|positive/i.test(word) ? "dir dir--up" : /deterior|negative/i.test(word) ? "dir dir--down" : "dir dir--flat";
  }
  function cap(s) { return s.charAt(0).toUpperCase() + s.slice(1); }

  /* gap ids by field (ids are generated; fields are stable) */
  var G = {
    pf: gapId("pf_ltm"), mergerDebt: gapId("merger_committed_debt_financing_amount"), guide: gapId("czr_financial_guidance_revenue_ebitda"),
    fy2324: gapId("total_debt_cash_fy2023_fy2024"), liq: gapId("liquidity_fy2023_fy2025"), cov: gapId("covenant_levels"),
    loan: gapId("loan_margins_prices"), spread: gapId("spread_to_treasury"), ltmRep: gapId("reported_ebitda_ltm"),
    addbacks: gapId("unrealized_addbacks"), mstar: gapId("morningstar_issuer_id"), ratings: gapId("issuer_ratings"),
    figi: gapId("figi"), fitch: gapId("rating_fitch"), outlook: gapId("rating_outlooks_moodys_sp"), closing: gapId("merger_expected_closing"),
    equity: gapId("equity_market_value")
  };
  var PROJ_REASON = "no RBOT projection exists (no run), and the sources carry no forecast" + (G.guide ? ": " + D.gaps[G.guide].reason.replace(/^not found in these files;\s*/, "") : "");
  function pfGap() { return gapD(G.pf); }
  function projGap() { return gapD(G.guide, PROJ_REASON); }

  /* ================================================================ the period spine */
  var GROUPS = [
    { key: "annual", label: "Annual", note: "actual" },
    { key: "interim", label: "Interim", note: "six months" },
    { key: "ltm", label: "Trailing", note: "base" },
    { key: "pf", label: "Pro forma", note: "" },
    { key: "proj", label: "Projected", note: "FY+1 to FY+3" }
  ];
  var STOPS = [
    { id: "fy2023", label: "FY2023", sub: "FY-2", group: "annual", col: "FY2023", bs: "FY2023", basis: "Year to 31 December 2023" },
    { id: "fy2024", label: "FY2024", sub: "FY-1", group: "annual", col: "FY2024", bs: "FY2024", basis: "Year to 31 December 2024" },
    { id: "fy2025", label: "FY2025", sub: "FY, last audited", group: "annual", col: "FY2025", bs: "FY2025", basis: "Year to 31 December 2025; balance sheet at 31 December 2025" },
    { id: "h1-2025", label: "H1 2025", sub: "PYTD", group: "interim", col: "H1 2025", bs: null, h1: "2025", basis: "Six months to 30 June 2025" },
    { id: "h1-2026", label: "H1 2026", sub: "YTD", group: "interim", col: "H1 2026", bs: "Q2 2026", h1: "2026", basis: "Six months to 30 June 2026; balance sheet at 30 June 2026" },
    { id: "ltm", label: "LTM Q2 2026", sub: "LTM, base period", group: "ltm", col: "LTM Q2 2026", bs: "Q2 2026", basis: "Twelve months to 30 June 2026; balance sheet at 30 June 2026" },
    { id: "pf-ltm", label: "PF-LTM", sub: "pro forma", group: "pf", basis: "LTM Q2 2026 pro forma for the Fertitta merger financing" },
    { id: "fy2026e", label: "FY2026E", sub: "FY+1", group: "proj", year: "2026", basis: "Year to 31 December 2026, projected" },
    { id: "fy2027e", label: "FY2027E", sub: "FY+2", group: "proj", year: "2027", basis: "Year to 31 December 2027, projected" },
    { id: "fy2028e", label: "FY2028E", sub: "FY+3", group: "proj", year: "2028", basis: "Year to 31 December 2028, projected" }
  ];
  var STOP_IX = {}; STOPS.forEach(function (s, i) { STOP_IX[s.id] = i; });
  var sel = STOP_IX.ltm;
  document.documentElement.style.setProperty("--stops", String(STOPS.length));

  /* dated events from the filings, pinned to the stop whose period holds them */
  var EVENTS = [
    { stop: "h1-2026", key: "issuer.merger.agreement_date", short: "Merger signed", label: "Merger agreement with Fertitta signed" },
    { stop: "fy2026e", key: "merger_go_shop_end", short: "Go-shop ends", label: "Go-shop period ends" },
    { stop: "fy2027e", key: "merger_initial_end_date", short: "End Date", label: "Merger End Date (initial)" },
    { stop: "fy2027e", key: "merger_ticking_fee_date", short: null, label: "Ticking fee accrues from" },
    { stop: "fy2027e", key: "merger_first_extended_end_date", short: null, label: "End Date, first extension" },
    { stop: "fy2027e", key: "merger_second_extended_end_date", short: null, label: "End Date, second extension" },
    { stop: "fy2028e", key: "cei_rcf_maturity", short: "RCF matures", label: "CEI Revolving Credit Facility matures" }
  ];
  var DUE = { "fy2026e": "debt_maturity_remaining_2026", "fy2027e": "debt_maturity_2027", "fy2028e": "debt_maturity_2028" };
  var INTEREST_EST = { "fy2026e": "cash_interest_fy2026e", "fy2027e": "guide_2027_interest" };

  /* ---- per-stop datum resolvers over the shared tables */
  function colOf(table, name) { return name ? table.columns.indexOf(name) : -1; }
  function finCell(row, st) {
    var i = colOf(T.financials, st.col);
    if (i >= 0) return row.cells[i];
    if (st.group === "pf") return pfGap();
    if (st.group === "proj") {
      if (/^Cash Interest/.test(row.label) && INTEREST_EST[st.id]) return withProj(fig(INTEREST_EST[st.id]));
      return projGap();
    }
    return gapD(null, "not reported for this period");
  }
  function bsCell(row, st) {
    var i = colOf(T.balanceSheet, st.bs);
    if (i >= 0) return row.cells[i];
    if (st.group === "pf") return pfGap();
    if (st.group === "proj") return projGap();
    return gapD(null, "the balance sheet at 30 June 2025 was not extracted (the pack carries 31 December 2025 and 30 June 2026)");
  }
  var COVER_KEYS = { "Interest Cover": "interest_cover_h1_", "Cash interest cover, debt only": "cash_interest_cover_h1_" };
  function cmCell(row, st) {
    var i = colOf(T.creditMetrics, st.col);
    if (i >= 0) return row.cells[i];
    if (st.group === "pf") return pfGap();
    if (st.group === "proj") return projGap();
    if (st.group === "interim") {
      if (COVER_KEYS[row.label]) return fig(COVER_KEYS[row.label] + st.h1);
      return gapD(null, st.h1 === "2026"
        ? "leverage is measured on LTM Adjusted EBITDA; at 30 June 2026 it is the LTM Q2 2026 figure"
        : "debt at 30 June 2025 was not extracted, and leverage is measured on LTM Adjusted EBITDA");
    }
    return gapD(null, "not reported for this period");
  }

  /* ---- tracks: the Model chart strip, re-cut to the spine's columns */
  function fromSpec(spec, interim) {
    return spec.series.map(function (ser, si) {
      return {
        label: ser.label, color: si === 0 ? "--chart-1" : "--chart-2", shape: si === 0 ? "circle" : "square",
        values: STOPS.map(function (st) {
          var i = spec.categories.indexOf(st.label);
          if (i >= 0) return ser.values[i];
          if (st.group === "pf") return pfGap();
          if (st.group === "proj") return projGap();
          return interim(ser.key, st);
        })
      };
    });
  }
  var TRACKS = [
    { id: "lev", title: D.charts.leverage.title, unit: "x", unitLabel: "x LTM Adj. EBITDA",
      series: fromSpec(D.charts.leverage, function (k, st) {
        return gapD(null, st.h1 === "2026" ? "leverage is measured on LTM Adjusted EBITDA; 30 June 2026 is shown at LTM Q2 2026" : "debt at 30 June 2025 was not extracted; leverage is an LTM measure");
      }) },
    { id: "cov", title: D.charts.coverage.title, unit: "x", unitLabel: "x",
      series: fromSpec(D.charts.coverage, function (k, st) { return fig((k === "cash" ? "cash_interest_cover_h1_" : "interest_cover_h1_") + st.h1); }) },
    { id: "liq", title: D.charts.liquidity.title, unit: "US$ m", unitLabel: "US$ m, period end",
      series: fromSpec(D.charts.liquidity, function (k, st) {
        if (st.h1 === "2026") return fig(k === "total" ? "liq_total" : "cash_2026_06_30");
        return gapD(null, "cash and liquidity at 30 June 2025 were not extracted");
      }) }
  ];

  function nice(x) { var p = Math.pow(10, Math.floor(Math.log10(x))), r = x / p; return (r <= 1 ? 1 : r <= 2 ? 2 : r <= 2.5 ? 2.5 : r <= 5 ? 5 : 10) * p; }
  function fmtTick(t, step) { var dp = step < 1 ? (step < 0.1 ? 2 : 1) : 0; return t.toLocaleString("en-US", { minimumFractionDigits: dp, maximumFractionDigits: dp }); }
  function labelOf(d, unit) { return unit === "x" ? d.v + "x" : String(d.v); }

  function drawTrack(tr) {
    var plot = tr.plot; clear(plot);
    var W = printW || Math.max(320, plot.clientWidth || 900), H = printW ? 70 : (plot.clientHeight || 78), n = STOPS.length, cw = W / n;
    var svg = sv("svg", { viewBox: "0 0 " + W + " " + H, width: W, height: H, role: "group", "aria-label": tr.title + " across the period spine; each value is focusable and opens its source" });
    var hid = "h-" + tr.id;
    svg.appendChild(sv("defs", {}, [sv("pattern", { id: hid, width: 6, height: 6, patternUnits: "userSpaceOnUse", patternTransform: "rotate(45)" }, [
      sv("rect", { width: 6, height: 6, fill: cssVar("--sheet", "#fff") }), sv("line", { x1: 0, y1: 0, x2: 0, y2: 6, stroke: cssVar("--grey-100", "#E1E3E6"), "stroke-width": 2 })])]));
    /* column bands: interim tinted, no-data stops hatched, the selected stop in soft blue */
    STOPS.forEach(function (st, i) {
      var fill = i === sel ? cssVar("--soft-blue-50", "#E7F5FF") : st.group === "interim" ? cssVar("--ground", "#F0F2F5") : (st.group === "pf" || st.group === "proj") ? "url(#" + hid + ")" : null;
      if (fill) svg.appendChild(sv("rect", { x: i * cw, y: 0, width: cw, height: H, fill: fill, "aria-hidden": "true" }));
      if (i > 0 && STOPS[i - 1].group !== st.group) svg.appendChild(sv("line", { x1: Math.round(i * cw) + 0.5, x2: Math.round(i * cw) + 0.5, y1: 0, y2: H, stroke: cssVar("--grey-200", "#C5C8CC"), "aria-hidden": "true" }));
    });
    var sx = sel * cw;
    svg.appendChild(sv("line", { x1: sx + 0.5, x2: sx + 0.5, y1: 0, y2: H, stroke: cssVar("--blue", "#0017E5"), "stroke-opacity": 0.45, "aria-hidden": "true" }));
    svg.appendChild(sv("line", { x1: sx + cw - 0.5, x2: sx + cw - 0.5, y1: 0, y2: H, stroke: cssVar("--blue", "#0017E5"), "stroke-opacity": 0.45, "aria-hidden": "true" }));

    /* scale: the strip's own range (as the caos strip, the axis need not hold zero for a line) */
    var vals = [];
    tr.series.forEach(function (s) { s.values.forEach(function (d) { if (!util.isGap(d)) vals.push(util.parseNum(d.v)); }); });
    var lo = Math.min.apply(null, vals), hi = Math.max.apply(null, vals);
    if (!isFinite(lo)) { lo = 0; hi = 1; }
    var span = hi - lo || Math.abs(hi) * 0.2 || 1;
    lo -= span * 0.22; hi += span * 0.22;
    var top = 17, bottom = H - 15;
    function y(v) { return bottom - (v - lo) / (hi - lo) * (bottom - top); }
    function x(i) { return (i + 0.5) * cw; }
    var step = nice((hi - lo) / 2.2), g = sv("g", { "aria-hidden": "true" });
    for (var t = Math.ceil(lo / step) * step; t <= hi + 1e-9; t += step) {
      var yy = Math.round(y(t)) + 0.5;
      g.appendChild(sv("line", { x1: 0, x2: W, y1: yy, y2: yy, stroke: cssVar("--grey-100", "#E1E3E6"), "stroke-dasharray": "2 3" }));
      g.appendChild(sv("text", { x: 4, y: yy - 3, class: "tick", text: fmtTick(t, step) + (tr.unit === "x" ? "x" : "") }));
    }
    svg.appendChild(g);

    /* the higher series labels above its points, the lower below */
    var means = tr.series.map(function (s) { var a = s.values.filter(function (d) { return !util.isGap(d); }).map(function (d) { return util.parseNum(d.v); }); return a.length ? a.reduce(function (p, q) { return p + q; }, 0) / a.length : 0; });
    var topIx = means.indexOf(Math.max.apply(null, means));
    tr.series.forEach(function (s, si) {
      var c = cssVar(s.color, "#0017E5"), above = si === topIx;
      var path = "";
      s.values.forEach(function (d, i) {
        if (util.isGap(d)) return;
        var prev = s.values[i - 1];
        path += (i > 0 && prev && !util.isGap(prev) ? "L" : "M") + x(i).toFixed(1) + " " + y(util.parseNum(d.v)).toFixed(1);
      });
      if (path) svg.appendChild(sv("path", { d: path, fill: "none", stroke: c, "stroke-width": 2, "aria-hidden": "true" }));
      s.values.forEach(function (d, i) {
        if (util.isGap(d)) return;
        var px = x(i), py = y(util.parseNum(d.v));
        var shape = s.shape === "square" ? sv("rect", { x: px - 3.6, y: py - 3.6, width: 7.2, height: 7.2, fill: c }) : sv("circle", { cx: px, cy: py, r: 4, fill: c });
        if (d.projected || d.prov === "model" || d.prov === "illustrative") shape.setAttribute("fill", "#fff"), shape.setAttribute("stroke", c), shape.setAttribute("stroke-width", 1.75);
        var lbl = sv("text", { x: px, y: above ? py - 8 : py + 15, "text-anchor": "middle", class: "lbl", text: labelOf(d, tr.unit) });
        mark(tr, svg, { x: px - 12, y: py - 12, w: 24, h: 24 }, s.label + ", " + STOPS[i].label + ": " + util.withUnit(d.v, tr.unit) + " (" + util.provWord(d) + ")", d.ref, [shape, lbl]);
      });
    });

    /* gaps: one labelled n/a per stop (or per span for the no-data stops), never a zero */
    var spans = {};
    STOPS.forEach(function (st, i) {
      var gaps = tr.series.map(function (s, si) { return { s: s, si: si, d: s.values[i] }; }).filter(function (o) { return util.isGap(o.d); });
      if (!gaps.length) return;
      if (st.group === "pf" || st.group === "proj") {
        if (spans[st.group]) { spans[st.group].to = i; return; }
        spans[st.group] = { from: i, to: i, d: gaps[0].d };
        return;
      }
      if (gaps.length === tr.series.length) {
        naMark(tr, svg, x(i), (top + bottom) / 2 + 4, "n/a", tr.title + ", " + st.label + ": n/a, " + gaps[0].d.reason, gaps[0].d.ref);
      } else {
        gaps.forEach(function (o) {
          var yy = o.si === topIx ? top + 2 : bottom + 4;
          naMark(tr, svg, x(i), yy, "n/a", o.s.label + ", " + st.label + ": n/a, " + o.d.reason, o.d.ref);
        });
      }
    });
    Object.keys(spans).forEach(function (k) {
      var sp = spans[k], cx = (sp.from + sp.to + 1) / 2 * cw, wide = (sp.to - sp.from + 1) * cw;
      var note = k === "pf" ? "no merger debt" : "no RBOT projection, no guidance";
      naMark(tr, svg, cx, (top + bottom) / 2 + 4, wide > 200 ? "n/a · " + note : "n/a", tr.title + ", " + STOPS[sp.from].label + (sp.to > sp.from ? " to " + STOPS[sp.to].label : "") + ": n/a, " + sp.d.reason, sp.d.ref, wide <= 200 ? note : null);
    });
    plot.appendChild(svg);
    plot.appendChild(tr.tip);
  }
  function naMark(tr, svg, cx, cy, text, label, ref, sub) {
    var t = sv("text", { x: cx, y: cy, "text-anchor": "middle", class: "na", text: text });
    var kids = [t];
    var w = Math.max(30, text.length * 6.2 + 8), h = 16;
    if (sub) { kids.push(sv("text", { x: cx, y: cy + 13, "text-anchor": "middle", class: "na-note", text: sub })); w = Math.max(w, sub.length * 5.6 + 8); h = 30; }
    mark(tr, svg, { x: cx - w / 2, y: cy - 12, w: w, h: h }, label, ref, kids);
  }
  function mark(tr, svg, box, label, ref, kids) {
    var g = sv("g", { class: "mark", tabindex: 0, role: "img", "aria-label": label, "data-ref": ref || null });
    kids.forEach(function (k) { g.appendChild(k); });
    var w = Math.max(24, box.w), h = Math.max(24, box.h);
    g.appendChild(sv("rect", { class: "hit", x: box.x + box.w / 2 - w / 2, y: box.y + box.h / 2 - h / 2, width: w, height: h, rx: 2 }));
    function show() {
      tr.tip.textContent = label + (ref ? ". Press Enter or click for the source." : "");
      tr.tip.hidden = false;
      var pr = tr.plot.getBoundingClientRect(), mr = g.getBoundingClientRect();
      var tw = Math.min(288, tr.tip.offsetWidth || 200);
      tr.tip.style.left = Math.min(Math.max(0, mr.left - pr.left + mr.width / 2 - tw / 2), pr.width - tw) + "px";
      var top = mr.top - pr.top - (tr.tip.offsetHeight || 40) - 6;
      tr.tip.style.top = (top < -40 ? mr.bottom - pr.top + 6 : top) + "px";
    }
    function hide() { tr.tip.hidden = true; }
    function press(e) { if (ref) { UI.open(ref, g); hide(); } else show(); if (e) e.preventDefault(); }
    g.addEventListener("mouseenter", show); g.addEventListener("mouseleave", hide);
    g.addEventListener("focus", show); g.addEventListener("blur", hide);
    g.addEventListener("click", press);
    g.addEventListener("keydown", function (e) { if (e.key === "Enter" || e.key === " ") press(e); if (e.key === "Escape") hide(); });
    svg.appendChild(g);
  }
  function keySwatch(s) {
    var c = cssVar(s.color, "#0017E5");
    var svg = sv("svg", { width: 18, height: 10, viewBox: "0 0 18 10", "aria-hidden": "true" }, [
      sv("line", { x1: 0, x2: 18, y1: 5, y2: 5, stroke: c, "stroke-width": 2 }),
      s.shape === "square" ? sv("rect", { x: 6, y: 2, width: 6, height: 6, fill: c }) : sv("circle", { cx: 9, cy: 5, r: 3.2, fill: c })
    ]);
    return el("li", {}, [svg, s.label]);
  }

  function buildSpine() {
    var host = $("spine");
    var spine = el("div", { class: "spine" });
    var twinBtn = el("button", { type: "button", class: "btn", "aria-expanded": "false", "aria-controls": "spine-twin", text: "Show as table" });
    spine.appendChild(el("div", { class: "spine__corner" }, [
      el("h2", { id: "spine-h", text: "Period spine" }),
      el("ul", { class: "spine__key" }, [
        el("li", {}, [el("span", { class: "sw sw--interim" }), "Interim, six months"]),
        el("li", {}, [el("span", { class: "sw sw--nodata" }), "No figures in this pack"]),
        el("li", {}, [el("span", { class: "pin-key" }), "Dated event, cited"])]),
      twinBtn
    ]));
    var col = 2;
    GROUPS.forEach(function (gr) {
      var n = STOPS.filter(function (s) { return s.group === gr.key; }).length;
      if (!n) return;
      var cell = el("div", { class: "spine__group" }, [el("b", { text: gr.label }), " " + gr.note]);
      cell.style.gridColumn = col + " / span " + n;
      spine.appendChild(cell);
      col += n;
    });
    var radios = el("div", { class: "stops", role: "radiogroup", "aria-label": "Period: the tracks, the period Snapshot, the Snapshot tables and the Model follow the selected stop" });
    STOPS.forEach(function (st, i) {
      var gap = st.group === "pf" || st.group === "proj";
      var b = el("button", { type: "button", role: "radio", class: "stop" + (gap ? " stop--gap" : ""), id: "stop-" + st.id, "data-i": i,
        "aria-checked": i === sel ? "true" : "false", tabindex: i === sel ? 0 : -1,
        "aria-label": st.label + ", " + st.sub + (gap ? ", figures not available in this pack" : "") }, [
        el("span", { class: "stop__label", text: st.label }), el("span", { class: "stop__sub", text: st.sub })]);
      b.style.gridColumn = String(i + 2);
      b.addEventListener("click", function () { select(i); });
      b.addEventListener("keydown", function (e) {
        var k = e.key, j = k === "ArrowRight" || k === "ArrowDown" ? i + 1 : k === "ArrowLeft" || k === "ArrowUp" ? i - 1 : k === "Home" ? 0 : k === "End" ? STOPS.length - 1 : null;
        if (j === null) return;
        e.preventDefault();
        select((j + STOPS.length) % STOPS.length, true);
      });
      radios.appendChild(b);
    });
    spine.appendChild(radios);
    STOPS.forEach(function (st, i) {
      var cell = el("div", { class: "pins", "data-i": i });
      cell.style.gridColumn = String(i + 2);
      var evs = EVENTS.filter(function (e) { return e.stop === st.id && e.short; });
      evs.forEach(function (e) {
        var d = fig(e.key);
        cell.appendChild(el("button", { type: "button", class: "pin", "data-ref": d.ref, "aria-label": e.label + ", " + d.v + ", cited " + d.ref, text: e.short }));
      });
      if (DUE[st.id]) {
        var due = fig(DUE[st.id]);
        cell.appendChild(el("button", { type: "button", class: "pin pin--due", "data-ref": due.ref, "aria-label": "Debt maturities due: " + due.v + " US$ m, cited " + due.ref, text: "Due " + due.v }));
      }
      spine.appendChild(cell);
    });
    var board = el("div", { class: "board" }, [spine]);
    TRACKS.forEach(function (tr) {
      tr.plot = el("div", { class: "track__plot" });
      tr.tip = el("div", { class: "chart__tip", role: "status", hidden: true });
      board.appendChild(el("div", { class: "track", id: "track-" + tr.id }, [
        el("div", { class: "track__label" }, [el("h3", {}, [tr.title + " ", el("span", { text: tr.unitLabel })]), el("ul", { class: "track__key", "aria-label": "Series" }, tr.series.map(keySwatch))]),
        tr.plot
      ]));
    });
    var twin = el("div", { class: "board__twin", id: "spine-twin", hidden: true }, [spineTwin()]);
    twinBtn.addEventListener("click", function () {
      var open = twinBtn.getAttribute("aria-expanded") !== "true";
      twinBtn.setAttribute("aria-expanded", String(open)); twinBtn.textContent = open ? "Hide table" : "Show as table"; twin.hidden = !open;
    });
    host.appendChild(el("div", { class: "spine-scroll" }, [board]));
    host.appendChild(twin);
    var last = 0;
    if (typeof ResizeObserver === "function") new ResizeObserver(function () { var w = board.clientWidth; if (Math.abs(w - last) < 2) return; last = w; drawTracks(); }).observe(board);
    if (document.fonts && document.fonts.ready) document.fonts.ready.then(drawTracks);
  }
  var printW = 0;
  function drawTracks() { TRACKS.forEach(drawTrack); }
  /* print lays the Front Page out at a fixed width, so the tracks are redrawn for it and scale as one image */
  function forPrint(on) { printW = on ? 1440 : 0; drawTracks(); }
  if (window.matchMedia) { var mq = window.matchMedia("print"); if (mq.addEventListener) mq.addEventListener("change", function (e) { forPrint(e.matches); }); }
  function spineTwin() {
    var t = el("table", { class: "dt dt--framed" });
    t.appendChild(el("caption", { class: "vh", text: "Period spine tracks as a table" }));
    t.appendChild(head([{ t: "Track and series" }].concat(STOPS.map(function (s) { return { t: s.label + " | " + s.sub, stops: s.id }; }))));
    var b = el("tbody");
    TRACKS.forEach(function (tr) {
      tr.series.forEach(function (s) {
        b.appendChild(el("tr", {}, [el("th", { scope: "row", text: tr.title + ": " + s.label + " (" + tr.unit + ")" })].concat(s.values.map(function (d, i) { return td(d, null, { "data-stops": STOPS[i].id }); }))));
      });
    });
    t.appendChild(b);
    return el("div", { class: "table-scroll" }, [t]);
  }

  /* ================================================================ masthead, nav counts */
  function buildMast() {
    var M = D.meta;
    $("title").textContent = "Credit Snapshot — " + M.issuer + " (" + M.ticker + ")";
    var meta = $("mast-meta");
    [M.pathway + ", " + M.depth + " depth", M.primaryLabel, "Reporting period " + M.reportingPeriod, "Analysis date " + M.analysisDate, M.runNote].forEach(function (s) { meta.appendChild(el("span", { text: s })); });
    $("nav-mods").textContent = String(D.modules.length);
    $("nav-ev").textContent = String(D.counts.cited + D.counts.calculated);
    $("nav-lim").textContent = String(D.limitations.length);
  }

  /* ================================================================ verdict band */
  function buildVerdict() {
    var v = $("verdict");
    var call = el("div", { class: "call" });
    D.meta.strategies.forEach(function (s) {
      var r = I.recommendation[s];
      call.appendChild(el("div", { class: "call__item" }, [el("span", { class: "call__label", text: s }), r ? UI.scale({ kind: "rec", pos: r.pos, word: r.word, illustrative: true, label: s }) : val(gapD(null, "no recommendation"))]));
    });
    call.appendChild(el("div", { class: "call__rule", "aria-hidden": "true" }));
    call.appendChild(el("div", { class: "call__item" }, [el("span", { class: "call__label", text: "Credit Score" }), UI.scale({ kind: "score", pos: I.creditScore.pos, illustrative: true, label: "Credit Score" })]));
    call.appendChild(el("div", { class: "call__item" }, [el("span", { class: "call__label", text: "Valuation" }), UI.scale({ kind: "val", pos: I.valuation.pos, illustrative: true, label: "Valuation" })]));
    call.appendChild(el("div", { class: "call__item" }, [el("span", { class: "call__label", text: "Direction · Outlook" }),
      el("span", { class: "call__dirs" }, [el("span", { class: dirClass(I.creditDirection.word), text: I.creditDirection.word }), el("span", { class: dirClass(I.sectorOutlook.word), text: I.sectorOutlook.word })])]));
    var w = I.weaknesses[0];
    var risk = el("p", { class: "risk-line" }, [el("b", { text: "Main risk" }), el("span", {}, [el("b", { text: w.label + ". ", style: "color:var(--navy)" }), judged(w.text, w.refs, false)])]);
    v.appendChild(el("section", { class: "v-call", "aria-labelledby": "v-call-h" }, [el("h2", { id: "v-call-h" }, ["The call", UI.illus()]), call, risk]));

    var ol = el("ol", { class: "findings" });
    I.keyFindings.forEach(function (k) { ol.appendChild(el("li", {}, [judged(k.text, k.refs, false)])); });
    v.appendChild(el("section", { class: "v-find", "aria-labelledby": "v-find-h" }, [el("h2", { id: "v-find-h" }, ["Key findings", UI.illus()]), ol]));

    v.appendChild(el("section", { class: "v-thesis", "aria-labelledby": "v-thesis-h" }, [
      el("h2", { id: "v-thesis-h" }, ["Investment thesis", UI.illus()]),
      el("p", { class: "thesis-text" }, [judged(I.thesis.text, I.thesis.refs, false)]),
      el("p", { class: "verdict__more" }, [el("a", { href: "#snapshot", text: "Full Credit Snapshot" }), txt(" · "), el("a", { href: "#analysis", text: "Analysis by module" })])
    ]));
  }

  /* ================================================================ period panel */
  var collected;
  function pcell(d, unit) { if (util.isGap(d) && (d.v === null || d.v === undefined)) collected.push(d); return td(d, unit); }
  function prow(label, d, unit, cls) { return el("tr", { class: cls || null }, [el("th", { scope: "row", text: label }), pcell(d, unit)]); }
  function ptable(caption, rows) { var t = el("table", { class: "dt" }); t.appendChild(el("caption", { class: "vh", text: caption })); var b = el("tbody"); rows.forEach(function (r) { b.appendChild(r); }); t.appendChild(b); return t; }
  function pblock(title, meta, kids) { return el("section", { class: "pblock" }, [el("h3", {}, [title, meta ? el("span", { text: meta }) : null])].concat(kids)); }
  function finRows(st) {
    return T.financials.rows.map(function (r) {
      var unit = /^%/.test(r.label) ? "%" : null;
      return prow(r.label, finCell(r, st), unit, r.kind === "sub" ? "sub" : r.kind === "total" ? "total" : null);
    });
  }
  function missingList(extra) {
    var seen = {}, items = [];
    collected.concat(extra || []).forEach(function (d) {
      var k = d.ref || d.reason; if (!k || seen[k]) return; seen[k] = true;
      items.push(el("li", {}, [d.ref ? UI.chip(d.ref) : el("b", { text: "n/a" }), txt(" " + cap(d.reason || "not in the sources"))]));
    });
    if (!items.length) return null;
    return el("ul", { class: "missing", "aria-label": "Missing for this period" }, [el("li", {}, [el("b", { text: "Missing here, with the reason" })])].concat(items));
  }
  function eventsFor(st) {
    var evs = EVENTS.filter(function (e) { return e.stop === st.id; });
    if (!evs.length) return el("p", { class: "note", text: "No dated event in the Source Pack falls in this period." });
    return el("ul", { class: "cat-list" }, evs.map(function (e) {
      return el("li", {}, [el("span", { class: "when" }, [val(fig(e.key))]), el("span", { text: e.label })]);
    }));
  }
  function moduleFor(refs) {
    return D.modules.filter(function (m) { return m.status === "Blocked" || (m.refs || []).some(function (r) { return refs.indexOf(r) >= 0; }); });
  }
  function adjRows(colName) {
    var A = T.ebitdaAdjustments, i = A.columns.indexOf(colName);
    return A.rows.map(function (r) { return prow(r.label, r.cells[i], null, r.kind === "total" ? "total" : r.kind === "sub" ? "sub" : r.kind === "indent" ? "indent" : null); });
  }
  function renderPeriod() {
    var st = STOPS[sel], host = clear($("period"));
    collected = [];
    var prev = el("button", { type: "button", class: "btn", disabled: sel === 0, text: sel > 0 ? "Previous: " + STOPS[sel - 1].label : "Previous" });
    var next = el("button", { type: "button", class: "btn", disabled: sel === STOPS.length - 1, text: sel < STOPS.length - 1 ? "Next: " + STOPS[sel + 1].label : "Next" });
    prev.addEventListener("click", function () { select(sel - 1); });
    next.addEventListener("click", function () { select(sel + 1); });
    host.appendChild(el("div", { class: "period__head" }, [
      el("h2", { id: "period-h", text: "Snapshot at " + st.label }),
      el("p", { text: st.basis + ". " + (st.group === "proj" || st.group === "pf" ? "Figures for this stop are not in the pack; what is known is shown with its source, and each gap with its reason." : "US$ m unless stated; every figure opens its source.") }),
      el("div", { class: "period__step" }, [prev, next])
    ]));
    var grid = el("div", { class: "period__grid" });
    var A, B, Cc;
    if (st.group === "annual" || st.group === "interim" || st.group === "ltm") {
      A = pblock("Earnings and cash flow", "US$ m", [ptable("Earnings and cash flow, " + st.label, finRows(st))]);
      var bsRows = T.balanceSheet.rows.map(function (r) { return prow(r.label, bsCell(r, st)); });
      var cmRows = T.creditMetrics.rows.map(function (r) { return prow(r.label, cmCell(r, st), "x"); });
      B = pblock("Balance sheet and credit metrics", st.bs ? "at " + (st.bs === "Q2 2026" ? "30 June 2026" : "31 December " + st.bs.slice(2)) : "period end", [ptable("Balance sheet, " + st.label, bsRows), ptable("Credit metrics, " + st.label, cmRows)]);
      var ckids = [];
      if (st.id === "ltm") {
        ckids.push(el("div", { class: "pblock__body" }, [el("p", { class: "subhead", text: "EBITDA adjustments, LTM Q2 2026" })]));
        ckids.push(ptable("EBITDA adjustments, LTM Q2 2026", adjRows("LTM Q2 2026")));
        ckids.push(el("div", { class: "pblock__body" }, [el("p", { class: "subhead", text: "Value and liquidity" })]));
        ckids.push(ptable("Value and liquidity", [
          prow("EV, merger transaction value", fig("ev_merger_usdm")), prow("EV / LTM Adj. EBITDA", fig("ev_multiple_ltm"), "x"),
          prow("Implied equity", fig("implied_equity_merger_usdm")), prow("Cash and revolver capacity", fig("liq_total"))]));
        Cc = pblock("Adjustments, value and events", null, ckids.concat([el("div", { class: "pblock__body" }, [el("p", { class: "subhead", text: "Events" }), eventsFor(STOPS[STOP_IX["h1-2026"]])])]));
      } else if (st.id === "h1-2026") {
        ckids.push(el("div", { class: "pblock__body" }, [el("p", { class: "subhead", text: "Events" }), eventsFor(st), el("p", { class: "subhead", text: "EBITDA adjustments, Q2 2026 (the quarter)" })]));
        ckids.push(ptable("EBITDA adjustments, Q2 2026", adjRows("Q2 2026")));
        Cc = pblock("Events and adjustments", null, ckids);
      } else {
        Cc = pblock("Events", null, [el("div", { class: "pblock__body" }, [eventsFor(st),
          st.id === "fy2025" || st.group === "annual" ? el("p", { class: "note" }, [txt("EBITDA adjustments are built for Q2 2026 and LTM Q2 2026 only. "), UI.chip(G.ltmRep)]) : null])]);
      }
    } else if (st.group === "pf") {
      var adjPf = T.ebitdaAdjustments.columns.indexOf("PF LTM");
      A = pblock("Transaction", "Primary: merger financing", [
        illusBand("Summary written for the mockup; the terms below are cited."),
        el("div", { class: "pblock__body" }, [el("p", {}, [judged(I.transactionSummary.text, I.transactionSummary.refs, false)])]),
        ptable("Merger terms", [
          prow("Cash per share (US$)", fig("merger_price_per_share_pr")), prow("Transaction value (US$ bn)", fig("merger_transaction_value")),
          prow("Assumed Caesars debt (US$ bn)", fig("merger_assumed_debt")), prow("Banks arranging new debt", fig("merger_financing_banks_count")),
          prow("New committed debt amount", gapD(G.mergerDebt))])]);
      B = pblock("Pro forma metrics", "PF-LTM", [ptable("Pro forma metrics", [
        prow("Structuring EBITDA, PF", adjPf >= 0 ? T.ebitdaAdjustments.rows.filter(function (r) { return /^Structuring/.test(r.label); })[0].cells[adjPf] : pfGap()),
        prow("Total debt, PF", pfGap()), prow("Total leverage, PF", pfGap(), "x"), prow("Net leverage, PF", pfGap(), "x"),
        prow("PF interest", T.capitalStructure.subtotals.pf_interest), prow("Interest cover, PF", pfGap(), "x")])]);
      var mods = moduleFor([G.pf, G.mergerDebt]);
      Cc = pblock("Why this stop is n/a", null, [el("div", { class: "pblock__body" }, [
        el("ul", {}, mods.map(function (m) { return el("li", {}, [el("b", { text: m.id + " " + m.name + " " }), UI.status(m.status), txt(" " + m.reason + " ")].concat(chips(m.refs))); })),
        el("p", { class: "note", text: "Closing is not dated in the sources; the End Dates sit on the FY2027E stop." })])]);
    } else {
      var rowsA = [prow("Debt maturities due in the year", fig(DUE[st.id]))];
      if (INTEREST_EST[st.id]) rowsA.push(prow(st.id === "fy2026e" ? "Cash interest on debt: H1 paid plus 10-Q estimate" : "Estimated interest payments (10-Q)", withProj(fig(INTEREST_EST[st.id]))));
      else rowsA.push(prow("Estimated interest payments", gapD(null, "the 10-Q estimates interest payments for the rest of 2026 and for 2027 only")));
      if (st.id === "fy2026e") {
        rowsA.push(prow("Capex guidance, rest of 2026, low", fig("guide_capex_remaining_2026_total_low")));
        rowsA.push(prow("Capex guidance, rest of 2026, high", fig("guide_capex_remaining_2026_total_high")));
      }
      A = pblock("Scheduled cash calls", "US$ m, from the filings", [ptable("Scheduled cash calls, " + st.label, rowsA)]);
      B = pblock("Projected metrics", st.sub, [ptable("Projected metrics, " + st.label, [
        prow("Net revenues", projGap()), prow("Adjusted EBITDA", projGap()), prow("FCF", projGap()),
        prow("Total leverage", projGap(), "x"), prow("Interest cover", projGap(), "x"), prow("Liquidity", projGap())])]);
      Cc = pblock("Events in " + st.year, null, [el("div", { class: "pblock__body" }, [eventsFor(st)])]);
    }
    [A, B, Cc].forEach(function (b) { grid.appendChild(b); });
    var miss = missingList();
    if (miss) Cc.appendChild(miss);
    host.appendChild(grid);
  }

  /* ================================================================ selection */
  function select(i, focus) {
    if (i < 0 || i >= STOPS.length) return;
    sel = i;
    document.querySelectorAll(".stop").forEach(function (b, j) {
      b.setAttribute("aria-checked", j === i ? "true" : "false"); b.tabIndex = j === i ? 0 : -1;
      if (j === i && focus) b.focus();
    });
    document.querySelectorAll(".pins").forEach(function (p) { p.classList.toggle("is-sel", Number(p.getAttribute("data-i")) === i); });
    $("nav-period").textContent = STOPS[i].label;
    drawTracks();
    renderPeriod();
    highlight();
  }
  function highlight() {
    var id = STOPS[sel].id;
    document.querySelectorAll("[data-stops]").forEach(function (n) {
      n.classList.toggle("col-hl", n.getAttribute("data-stops").split(" ").indexOf(id) >= 0);
    });
  }
  /* which stops a table column belongs to */
  function stopsFor(colName) {
    var out = STOPS.filter(function (s) { return s.col === colName; }).map(function (s) { return s.id; });
    if (colName === "Q2 2026") out = ["h1-2026", "ltm"];
    if (colName === "PF LTM") out = ["pf-ltm"];
    if (colName === "LTM Q2 2026" && out.indexOf("ltm") < 0) out.push("ltm");
    return out.join(" ") || null;
  }

  /* ================================================================ Credit Snapshot blocks */
  var ADJ_STOPS = { "Q2 2026": "h1-2026", "LTM Q2 2026": "ltm", "PF LTM": "pf-ltm" };
  function periodTable(t, caption, unitFor) {
    var map = t === T.ebitdaAdjustments ? function (c) { return ADJ_STOPS[c] || null; } : t === T.segments ? function () { return null; } : stopsFor;
    var tb = el("table", { class: "dt" });
    tb.appendChild(el("caption", { class: "vh", text: caption }));
    tb.appendChild(head([{ t: t.unit }].concat(t.columns.map(function (c) { return { t: c, stops: map(c), num: true }; }))));
    var b = el("tbody");
    t.rows.forEach(function (r) {
      b.appendChild(el("tr", { class: r.kind === "sub" ? "sub" : r.kind === "total" ? "total" : r.kind === "indent" ? "indent" : null },
        [el("th", { scope: "row", text: r.label })].concat(r.cells.map(function (d, i) { return td(d, unitFor ? unitFor(r) : null, { "data-stops": map(t.columns[i]) }); }))));
    });
    tb.appendChild(b);
    return el("div", { class: "table-scroll" }, [tb]);
  }
  function buildSnapshot() {
    var S = $("snap");
    /* 1 Company profile */
    var tracePairs = T.trace.rows.filter(function (r) { return r.issuer === D.meta.ticker; });
    var ratingsCell = frag([el("span", { text: "Issuer: " }), val(gapD(G.ratings)), el("br")].concat(tracePairs.map(function (r) {
      return frag([el("span", { text: r.seniority + " " + r.maturity.v + ": " }), val(r.moodys), txt(" / "), val(r.sp), el("br")]);
    })).concat([el("span", { text: "Fitch: " }), val(gapD(G.fitch))]));
    var left = kvTable("Company profile, identifiers", [
      kvRow("Issuer", val(fig("issuer.name"))),
      kvRow("Ticker", val(fig("issuer.ticker"))),
      kvRow("Morningstar Issuer ID", val(gapD(G.mstar))),
      kvRow("Sector / Country", val(gapD(null, "sector and country classification are not in the extracted figures"))),
      kvRow("Shareholders", frag([el("span", { text: "Carano family, about " }), val(fig("merger_carano_stake"), "%"), el("br"), el("span", { text: "Pending sale to " }), val(fig("issuer.merger.acquirer_brand"))])),
      kvRow("Corp Ratings (M/S/F)", ratingsCell),
      kvRow("Outlook (M/S/F)", val(gapD(G.outlook)))
    ]);
    var right = kvTable("Company profile, management and views", [
      kvRow("Management", frag([el("span", { text: "CEO " }), val(fig("issuer.ceo")), el("br"), el("span", { text: "CFO " }), val(fig("issuer.cfo")), el("br"), el("span", { text: "President and COO " }), val(fig("issuer.president_coo"))])),
      kvRow("Sector Outlook", frag([el("span", { class: dirClass(I.sectorOutlook.word), text: I.sectorOutlook.word }), UI.illus()])),
      kvRow("Sponsor Quality", frag([el("span", { class: "prov-model", text: I.sponsorQuality.word }), UI.illus(), el("br"), el("span", { class: "note prov-model", text: I.sponsorQuality.basis })])),
      kvRow("Credit Score", frag([UI.scale({ kind: "score", pos: I.creditScore.pos, illustrative: true, label: "Credit Score" }), UI.illus()])),
      kvRow("Credit Direction", frag([el("span", { class: dirClass(I.creditDirection.word), text: I.creditDirection.word }), UI.illus()]))
    ]);
    S.appendChild(block("snap-profile", "Company profile", D.meta.issuer, [el("div", { class: "kv2" }, [left, right])]));

    /* 2 Analyst recommendation */
    var recRows = [kvRow("Analyst", frag([el("span", { text: D.meta.analyst.v }), UI.illus()])), kvRow("Date", el("span", { class: "num", text: D.meta.analysisDate }))];
    D.meta.strategies.forEach(function (s) { var r = I.recommendation[s]; recRows.push(kvRow(s, UI.scale({ kind: "rec", pos: r.pos, word: r.word, illustrative: true, label: s }))); });
    recRows.push(kvRow("Valuation", UI.scale({ kind: "val", pos: I.valuation.pos, illustrative: true, label: "Valuation" })));
    S.appendChild(block("snap-rec", "Analyst recommendation", "per Strategy", [illusBand("No RBOT run exists: the recommendation, score and valuation are written for the mockup."), kvTable("Analyst recommendation", recRows)]));

    /* 3 Transaction summary and new debt issues (Primary flag on) */
    if (D.meta.primary) {
      var terms = kvTable("Merger terms", [
        kvRow("Agreement date", val(fig("issuer.merger.agreement_date"))),
        kvRow("Acquirer", frag([val(fig("issuer.merger.acquirer_brand")), txt(" via "), val(fig("issuer.merger.parent"))])),
        kvRow("Cash per share (US$)", val(fig("merger_price_per_share_pr"))),
        kvRow("Transaction value incl. assumed debt (US$ bn)", val(fig("merger_transaction_value"))),
        kvRow("Assumed debt (US$ bn)", val(fig("merger_assumed_debt")))
      ]);
      var terms2 = kvTable("Merger terms, continued", [
        kvRow("Financing", val(fig("issuer.merger.financing"))),
        kvRow("Financing condition", val(fig("issuer.merger.financing_condition"))),
        kvRow("Termination fee / reverse fee (US$)", frag([val(fig("merger_termination_fee")), txt(" / "), val(fig("merger_reverse_termination_fee"))])),
        kvRow("End Date", frag([val(fig("merger_initial_end_date")), txt(", extendable to "), val(fig("merger_first_extended_end_date")), txt(" and "), val(fig("merger_second_extended_end_date"))])),
        kvRow("Expected closing", val(gapD(G.closing)))
      ]);
      var tr = el("table", { class: "dt" });
      tr.appendChild(el("caption", { class: "vh", text: "New debt issues" }));
      tr.appendChild(head(["Borrower", "Bloomberg ID (FIGI)", "Instrument", "Debt type", "UoP", { t: "Tranche size | US$ m", num: true }, "Guidance / IPT", "OID", "Maturity", "Exp. ratings", "CR score", "Commit date"].map(function (c) { return typeof c === "string" ? { t: c, text: true } : c; })));
      var md = gapD(G.mergerDebt);
      tr.appendChild(el("tbody", {}, [el("tr", {}, [tdText(md), tdText(gapD(G.figi)),
        el("td", {}, [el("span", { text: "New committed debt financing, " }), val(fig("merger_financing_banks_count")), el("span", { text: " banks" })]),
        tdText(md), el("td", {}, [el("span", { text: "Acquisition " }), UI.chip(fig("issuer.merger.financing").ref)]),
        td(md), tdText(md), tdText(md), tdText(md), tdText(md), tdText(md), tdText(md)])]));
      S.appendChild(block("snap-transaction", "Transaction summary and new debt issues", D.meta.primaryLabel, [
        illusBand("Summary written for the mockup; every term in the table is cited."),
        el("div", { class: "block__body" }, [el("p", { class: "prose" }, [judged(I.transactionSummary.text, I.transactionSummary.refs, false)])]),
        el("div", { class: "kv2" }, [terms, terms2]),
        el("div", { class: "bar bar--sub", text: "New debt issues" }),
        el("div", { class: "table-scroll" }, [tr])
      ], "span-2"));
    }

    /* 4 Capital structure */
    S.appendChild(block("snap-capital", "Capital structure", "at " + T.capitalStructure.asOf + "; multiples on LTM Adj. EBITDA", [
      el("div", { class: "table-scroll" }, [capTable()]),
      el("p", { class: "note", style: "padding:0 var(--s-3)" }, [txt(T.capitalStructure.ebitda_basis.replace(/\s*\[K\d+\]/, "") + " "), UI.chip(fig("ltm_adj_ebitda_q2_2026").ref), UI.chip(G.addbacks)]),
      el("div", { class: "chart-row" }, [chartInto("stackedColumns", D.charts.maturityWall, "c-snap-wall"), chartInto("columns", stackSpec(), "c-snap-stack")])
    ], "span-2"));

    /* 5 Business description · EBITDA adjustments */
    S.appendChild(block("snap-business", "Business description", null, [illusBand("Written for the mockup from the cited figures."), el("div", { class: "block__body" }, [el("p", { class: "prose" }, [judged(I.businessDescription.text, I.businessDescription.refs, false)])]),
      kvTable("Segments", T.segments.rows.slice(0, 4).map(function (r) { return kvRow(r.label + ", Q2 2026 net revenues (US$ m)", val(r.cells[1])); }))]));
    S.appendChild(block("snap-adjustments", "EBITDA adjustments", "Reported to Structuring to SSIM", [periodTable(T.ebitdaAdjustments, "EBITDA adjustments"), el("p", { class: "note", style: "padding:0 var(--s-3) var(--s-3)", text: T.ebitdaAdjustments.note })]));

    /* 6 Investment thesis · Catalysts */
    S.appendChild(block("snap-thesis", "Investment thesis", null, [illusBand("No RBOT run exists: the thesis is written for the mockup from the cited figures."), el("div", { class: "block__body" }, [el("p", { class: "prose" }, [judged(I.thesis.text, I.thesis.refs, false)])])]));
    S.appendChild(block("snap-catalysts", "Catalysts and near-term events", null, [illusBand("Selection written for the mockup; dates are cited."), el("div", { class: "block__body" }, [
      el("ul", { class: "cat-list" }, I.catalysts.map(function (c) { return el("li", {}, [el("span", { class: "when", text: stopForRefs(c.refs) }), el("span", {}, [judged(c.text, c.refs, false)])]); }))])]));

    /* 7 Credit summary */
    function swList(items) { return el("ul", { class: "sw-list" }, items.map(function (s) { return el("li", {}, [el("b", { text: s.label }), el("span", {}, [judged(s.text, s.refs, false)])]); })); }
    S.appendChild(block("snap-credit-summary", "Credit summary", null, [
      illusBand("Strengths, weaknesses, the performance read and the risk register are written for the mockup; every figure in them is cited."),
      el("div", { class: "grid2", style: "gap:0" }, [
        el("div", {}, [el("div", { class: "bar bar--sub", text: "Strengths" }), swList(I.strengths)]),
        el("div", { style: "border-left:var(--rule)" }, [el("div", { class: "bar bar--sub", text: "Weaknesses" }), swList(I.weaknesses)])]),
      el("div", { class: "bar bar--sub", text: "Historical performance" }),
      el("div", { class: "block__body" }, [el("p", { class: "prose" }, [judged(I.historicalPerformance.text, I.historicalPerformance.refs, false)])]),
      el("div", { class: "chart-row" }, [chartInto("columns", D.charts.revenueEbitda, "c-snap-rev"), chartInto("riskMatrix", D.charts.risk, "c-snap-risk")])
    ], "span-2"));

    /* 8 Financials */
    S.appendChild(block("snap-financials", "Financials", "US$ m; FY-2, FY-1, FY, PYTD, YTD, LTM; negatives in parentheses as filed", [periodTable(T.financials, "Financials", function (r) { return /^%/.test(r.label) ? "%" : null; }), el("p", { class: "note", style: "padding:0 var(--s-3) var(--s-3)", text: T.financials.note })], "span-2"));

    /* 9 Balance sheet · Credit metrics */
    S.appendChild(block("snap-balance", "Balance sheet", "US$ m, period end", [periodTable(T.balanceSheet, "Balance sheet")]));
    S.appendChild(block("snap-metrics", "Credit metrics", "x", [periodTable(T.creditMetrics, "Credit metrics"), el("p", { class: "note", style: "padding:0 var(--s-3) var(--s-3)", text: T.creditMetrics.note })]));

    /* 10 Loan RV · HY RV */
    S.appendChild(block("snap-loan-rv", "Loan relative value", "Source: Bloomberg US Leveraged Loan Index", [loanRv()], "span-2"));
    S.appendChild(block("snap-hy-rv", "High-yield relative value", "Source: Bloomberg US Corporate High Yield Index", [hyRv()], "span-2"));
    S.appendChild(block("snap-rv-charts", "Relative value charts", "TRACE last trades and Q2 2026 peer releases", [el("div", { class: "chart-row", style: "border-top:0" }, [chartInto("scatter", D.charts.yieldCurve, "c-snap-yield"), chartInto("rangeStrip", D.charts.peerRange, "c-snap-peer")])], "span-2"));
  }
  function stopForRefs(refs) {
    var d = null;
    refs.forEach(function (r) { var c = D.citations[r]; if (!d && c && /\d{4}/.test(c.value || "") && /date|end|fee/i.test(c.key)) d = c.value; });
    return d || "Not dated";
  }
  function shortFacility(f) {
    return f.replace(/^CEI /, "").replace("Revolving Credit Facility", "RCF").replace("Delayed Draw Term Loan", "DDTL").replace("Senior Secured Notes", "SSN")
      .replace("Senior Notes", "SN").replace("Special Improvement District Bonds", "SID bonds").replace("Long-term notes and other payables", "Other payables");
  }
  function stackSpec() {
    var rows = T.capitalStructure.rows;
    return {
      title: "Cumulative leverage through the debt stack", unit: "x", categoryLabel: "Facility, in order of rank",
      categories: rows.map(function (r) { return shortFacility(r.facility); }),
      series: [{ key: "cum", label: "Cumulative Structuring multiple", values: rows.map(function (r) { return r.structuring_multiple; }) }],
      summary: "Secured debt reaches " + rows.filter(function (r) { return r.rank === "secured"; }).slice(-1)[0].structuring_multiple.v + "x of LTM Adjusted EBITDA; the full stack reaches " + rows.slice(-1)[0].structuring_multiple.v + "x.",
      source: "Caesars Q2 2026 10-Q debt table; LTM Adjusted EBITDA; calculations by build-data.py", height: 220
    };
  }
  function capTable() {
    var cs = T.capitalStructure, t = el("table", { class: "dt" });
    t.appendChild(el("caption", { class: "vh", text: "Capital structure at " + cs.asOf }));
    t.appendChild(head([{ t: "Facility", text: true }, { t: "Debt type", text: true }, { t: "Bloomberg ID (FIGI)", text: true }, { t: "Facility ratings | M / S", text: true }, { t: "Spread / Coupon | %", num: true }, { t: "CCY", text: true }, { t: "Maturity", text: true },
      { t: "Bid", num: true }, { t: "Ask", num: true }, { t: "Outstanding | US$ m", num: true }, { t: "Structuring multiple | x", num: true }, { t: "SSIM multiple | x", num: true }, { t: "% EV", num: true }, { t: "Recommendation", text: true }]));
    var b = el("tbody"), recs = {};
    I.byInstrument.forEach(function (r) { recs[r.facility] = r; });
    function row(r) {
      var rec = recs[r.facility];
      b.appendChild(el("tr", {}, [el("th", { scope: "row", text: r.facility }), el("td", { text: r.debtType }), tdText(r.figi), tdText(r.ratings), td(r.coupon), el("td", { text: r.ccy }), tdText(r.maturity),
        td(r.bid), td(r.ask), td(r.outstanding), td(r.structuring_multiple), td(r.ssim_multiple), td(r.pct_ev),
        el("td", { class: "rec-cell" }, rec ? [UI.scale({ kind: "rec", pos: rec.pos, word: rec.word, illustrative: true, label: r.facility })] : [])]));
    }
    function sub(label, d, cls, extra) {
      var r = el("tr", { class: cls || "total" }, [el("th", { scope: "row", colspan: 9, style: "text-align:right", text: label }), td(d)]);
      (extra || [null, null, null]).forEach(function (x) { r.appendChild(x ? td(x) : el("td")); });
      r.appendChild(el("td"));
      b.appendChild(r);
    }
    var st = cs.subtotals, rows = cs.rows;
    var lastOf = function (rank) { var a = rows.filter(function (r) { return r.rank === rank; }); return a[a.length - 1]; };
    rows.filter(function (r) { return r.rank === "secured"; }).forEach(row);
    var ls = lastOf("secured");
    sub("Senior secured debt", st.senior_secured, "total", [ls.structuring_multiple, ls.ssim_multiple, ls.pct_ev]);
    rows.filter(function (r) { return r.rank === "unsecured"; }).forEach(row);
    var lu = lastOf("unsecured");
    sub("Unsecured debt", st.unsecured, "total", [lu.structuring_multiple, lu.ssim_multiple, lu.pct_ev]);
    rows.filter(function (r) { return r.rank === "other"; }).forEach(row);
    var lo = rows[rows.length - 1];
    sub("Total debt", st.total_debt, "total", [lo.structuring_multiple, lo.ssim_multiple, lo.pct_ev]);
    sub("Cash", st.cash, "sub");
    sub("(Implied) Equity, at the merger value", st.implied_equity, "sub");
    sub("Equity, listed market value", st.equity_market_value, "sub");
    sub("EV, merger transaction value", st.ev, "total", [st.ev_multiple, null, null]);
    sub("PF interest", st.pf_interest, "sub");
    t.appendChild(b);
    return t;
  }
  function loanRv() {
    var idx = el("table", { class: "dt" });
    idx.appendChild(el("caption", { class: "vh", text: "Loan index statistics" }));
    idx.appendChild(head([{ t: "Index statistics", text: true }, { t: "Ba · Ba/B · B · Caa", text: true }]));
    idx.appendChild(el("tbody", {}, [el("tr", {}, [el("th", { scope: "row", text: "Bloomberg ID, market value, avg price, Δ1M, ΔYTD, YTM, 3Y DM" }), tdText(gapD(null, "Bloomberg US Leveraged Loan Index statistics are not in the Source Pack"))])]));
    var cmp = el("table", { class: "dt" });
    cmp.appendChild(el("caption", { class: "vh", text: "Loan comparables" }));
    cmp.appendChild(head([{ t: "Facility", text: true }, { t: "FIGI", text: true }, { t: "Ratings", text: true }, { t: "Size | US$ m", num: true }, { t: "Margin", num: true }, { t: "Maturity", text: true }, { t: "Seniority", text: true }, { t: "Mid", num: true }, { t: "Δ1M", num: true }, { t: "ΔYTD", num: true }, { t: "Mid YTM", num: true }, { t: "Mid 3Y DM", num: true }]));
    var b = el("tbody"), lp = gapD(G.loan);
    T.capitalStructure.rows.filter(function (r) { return /Term Loan/.test(r.debtType); }).forEach(function (r) {
      b.appendChild(el("tr", {}, [el("th", { scope: "row", text: r.facility }), tdText(r.figi), tdText(r.ratings), td(r.outstanding), td(lp), tdText(r.maturity), el("td", { text: "1L, secured" }), td(lp), td(lp), td(lp), td(lp), td(lp)]));
    });
    b.appendChild(el("tr", {}, [el("th", { scope: "row", text: "Peer loans (MGM, PENN)" }), el("td", { colspan: 11 }, [val(gapD(null, "no peer loan quotes in the Source Pack; TRACE covers bonds only"))])]));
    cmp.appendChild(b);
    return frag([el("div", { class: "table-scroll" }, [idx]), el("div", { class: "table-scroll" }, [cmp])]);
  }
  function hyRv() {
    var idx = el("table", { class: "dt" });
    idx.appendChild(el("caption", { class: "vh", text: "High-yield index statistics" }));
    idx.appendChild(head([{ t: "Index statistics", text: true }, { t: "Ba · Ba/B · B · Caa", text: true }]));
    idx.appendChild(el("tbody", {}, [el("tr", {}, [el("th", { scope: "row", text: "Bloomberg ID, avg coupon, market value, avg price, Δ1M, ΔYTD, YTW, OAS" }), tdText(gapD(null, "Bloomberg US Corporate High Yield Index statistics are not in the Source Pack"))])]));
    var cmp = el("table", { class: "dt" });
    cmp.appendChild(el("caption", { class: "vh", text: "High-yield comparables" }));
    cmp.appendChild(head([{ t: "Company", text: true }, { t: "CUSIP | FIGI n/a", text: true }, { t: "Ratings | M / S", text: true }, { t: "Size | US$ m", num: true }, { t: "Coupon | %", num: true }, { t: "Maturity", text: true }, { t: "Seniority", text: true }, { t: "Mid | last trade", num: true }, { t: "Δ1M", num: true }, { t: "ΔYTD", num: true }, { t: "Yield | last, %", num: true }, { t: "OAS", num: true }]));
    var b = el("tbody"), sizeBy = {};
    T.capitalStructure.rows.forEach(function (r) { var yr = r.facility.match(/(\d{4})$/); if (r.coupon && r.coupon.v && yr) sizeBy[parseFloat(r.coupon.v) + "|" + yr[1]] = r.outstanding; });
    T.trace.rows.forEach(function (r) {
      var size = sizeBy[parseFloat(r.coupon.v) + "|" + String(r.maturity.v || "").slice(-4)];
      var isIssuer = r.issuer === D.meta.ticker;
      b.appendChild(el("tr", {}, [el("th", { scope: "row", text: r.issuer }), el("td", { text: r.cusip }), el("td", { class: "rec-cell" }, [val(r.moodys), txt(" / "), val(r.sp)]),
        td(size || gapD(null, isIssuer ? "size not matched to the debt table" : "peer issue size is not in the sources")), td(r.coupon), tdText(r.maturity),
        isIssuer ? el("td", { text: r.seniority }) : el("td", {}, [el("span", { class: "prov-model", text: r.seniority }), el("span", { class: "tag-model", text: "Model" })]),
        td(r.price), td(gapD(null, "one TRACE observation per bond; no history in the pack")), td(gapD(null, "one TRACE observation per bond; no history in the pack")), td(r.yield), td(gapD(G.spread))]));
    });
    cmp.appendChild(b);
    return frag([el("div", { class: "table-scroll" }, [idx]), el("div", { class: "table-scroll" }, [cmp]), el("p", { class: "note", style: "padding:var(--s-2) var(--s-3)", text: T.trace.note })]);
  }

  /* ================================================================ analysis by module */
  function liquiditySpec() {
    var rows = T.liquidity.rows;
    var short = function (l) {
      return /^Cash/.test(l) ? "Cash" : /CEI Revolving/.test(l) ? "CEI RCF" : /CVA/.test(l) ? "CVA RCF" : /letters of credit/.test(l) ? "LCs" : /reserves/.test(l) ? "Reserves" : /regulatory/.test(l) ? "Regulatory" : /^Total/.test(l) ? "Total" : l;
    };
    return {
      title: "Liquidity bridge at 30 June 2026", unit: "US$ m", categoryLabel: "Step",
      summary: "Cash of " + rows[0].cell.v + " plus revolver capacity, less letters of credit, reserves and regulatory holds, gives " + rows[rows.length - 1].cell.v + " of liquidity; the bridge reconciles.",
      steps: rows.map(function (r, i) { return { label: r.label, short: short(r.label), kind: i === 0 || i === rows.length - 1 ? "total" : "delta", d: r.cell }; }),
      source: "Caesars Q2 2026 earnings release, liquidity table"
    };
  }
  var MODULE_VIEW = {
    "CP-0": { lead: null, detail: function () { return [limitationsTable(D.limitations.filter(function (l) { return l.origin === "czr.json"; }), "Source Pack gaps logged at intake")]; } },
    "CP-1": { lead: ["columns", "revenueEbitda"], detail: function () { return [el("div", { class: "grid2" }, [chartInto("waterfall", liquiditySpec(), "c-cp1-liq"), chartInto("stackedColumns", D.charts.maturityWall, "c-cp1-wall")]), el("p", { class: "prose" }, [judged(I.historicalPerformance.text, I.historicalPerformance.refs)])]; } },
    "CP-1A": { lead: ["dumbbell", "segments"], detail: function () { return [el("p", { class: "prose" }, [judged(I.businessDescription.text, I.businessDescription.refs)]), periodTable(T.segments, "Segments")]; } },
    "CP-1B": { lead: ["dumbbell", "segments"], detail: function () { return [periodTable(T.segments, "Segments"), chartInto("waterfall", D.charts.ebitdaBridge, "c-cp1b-bridge")]; } },
    "CP-1D": { lead: ["waterfall", "ebitdaBridge"], detail: function () { return [periodTable(T.ebitdaAdjustments, "EBITDA adjustments")]; } },
    "CP-2": { lead: ["lineStrip", "interestPath"], detail: function () { return [el("div", { class: "grid2" }, [chartInto("waterfall", D.charts.cashBridge, "c-cp2-cash"), chartInto("waterfall", liquiditySpec(), "c-cp2-liq")]), el("p", { class: "prose" }, [judged(I.strengths[1].text, I.strengths[1].refs)])]; } },
    "CP-2A": { lead: ["riskMatrix", "risk"], detail: function () { return [el("ul", { class: "sw-list" }, I.weaknesses.map(function (w) { return el("li", {}, [el("b", { text: w.label }), el("span", {}, [judged(w.text, w.refs)])]); }))]; } },
    "CP-3": { lead: ["scatter", "yieldCurve"], detail: function () {
      return [el("div", { class: "grid2" }, [chartInto("rangeStrip", D.charts.peerRange, "c-cp3-peer"), el("div", {}, [illusBand("Score, valuation and per-instrument calls are written for the mockup."),
        kvTable("Score and valuation", [kvRow("Credit Score", UI.scale({ kind: "score", pos: I.creditScore.pos, illustrative: true, label: "Credit Score" })), kvRow("Valuation", UI.scale({ kind: "val", pos: I.valuation.pos, illustrative: true, label: "Valuation" }))].concat(
          I.byInstrument.filter(function (r) { return r.pos; }).map(function (r) { return kvRow(r.facility, UI.scale({ kind: "rec", pos: r.pos, word: r.word, illustrative: true, label: r.facility })); })))])]),
        el("p", { class: "prose" }, [judged(I.thesis.text, I.thesis.refs)])];
    } },
    "CP-4": { lead: ["bullet", "covenant"], detail: function () { return [el("p", { class: "prose" }, [txt("The CEI revolver matures on "), val(fig("cei_rcf_maturity")), txt(", after the merger's latest End Date of "), val(fig("merger_second_extended_end_date")), txt(". No maintenance covenant level is cited, so headroom is an n/a gap "), UI.chip(G.cov), txt(".")])]; } },
    "CP-5": { lead: null, detail: function () { return [el("p", { class: "prose" }, [txt(D.counts.cited + " cited figures, " + D.counts.calculated + " calculations, " + D.counts.gaps + " logged gaps and " + D.counts.synthetic_sources + " synthetic portfolio rows. "), el("a", { href: "#evidence", text: "Open the evidence register" }), txt(".")])]; } },
    "CP-6": { lead: null, detail: null }
  };
  var MODULE_FIGS = {
    "CP-1": [["ltm_net_revenues_q2_2026", "Net revenues, LTM"], ["ltm_adj_ebitda_q2_2026", "Adj. EBITDA, LTM"], ["total_debt_face_2026_06_30", "Total debt, face"], ["net_debt_calc_2026_06_30", "Net debt"], ["liq_total", "Cash and revolver capacity"], ["total_leverage_ltm", "Total leverage", "x"]],
    "CP-1A": [["net_revenues_q2_2026", "Net revenues, Q2 2026"], ["adj_ebitda_q2_2026", "Adj. EBITDA, Q2 2026"], ["merger_transaction_value", "Merger value (US$ bn)"]],
    "CP-1B": [["net_revenues_q2_2026", "Net revenues, Q2 2026"], ["net_revenues_q2_2025", "Net revenues, Q2 2025"], ["adj_ebitda_q2_2026", "Adj. EBITDA, Q2 2026"], ["adj_ebitda_q2_2025", "Adj. EBITDA, Q2 2025"], ["net_income_attrib_q2_2026", "Net loss attributable, Q2 2026"]],
    "CP-1D": [["reported_ebitda_q2_2026", "Reported EBITDA, Q2 2026"], ["structuring_ebitda_q2_2026", "Structuring EBITDA, Q2 2026"], ["ltm_adj_ebitda_q2_2026", "Structuring EBITDA, LTM"]],
    "CP-2": [["ffo_ltm", "FFO, LTM"], ["fcf_ltm", "FCF, LTM"], ["guide_remaining_2026_interest", "Estimated interest, rest of 2026"], ["guide_2027_interest", "Estimated interest, 2027"], ["debt_maturity_2027", "Debt due 2027"], ["cash_2026_06_30", "Cash, 30 June 2026"]],
    "CP-3": [["trace_czr_12769gac4_last_price", "Secured 2032s, last price"], ["trace_czr_12769gac4_last_yield", "Secured 2032s, last yield", "%"], ["trace_czr_12769gad2_last_price", "Unsecured 2032s, last price"], ["trace_czr_12769gad2_last_yield", "Unsecured 2032s, last yield", "%"], ["trace_yield_median", "Median yield, four bonds", "%"], ["ev_multiple_ltm", "EV / LTM Adj. EBITDA", "x"]],
    "CP-4": [["cei_rcf_maturity", "CEI revolver matures"], ["merger_second_extended_end_date", "Latest merger End Date"], ["senior_secured_debt_2026_06_30", "Senior secured debt"], ["net_leverage_ltm", "Net leverage, LTM", "x"]]
  };
  function moduleFigs(m) {
    var list = MODULE_FIGS[m.id];
    if (m.id === "CP-6" && /portfolio/i.test(m.name)) {
      var P = D.portfolio.summary;
      return kvTable(m.id + " key figures", ["Max Single Issuer", "Weighted Average Rating (WAR)", "1st Lien Exposure (% NAV)", "Max Single Sector"].filter(function (k) { return P[k]; }).map(function (k) { return el("tr", {}, [el("th", { scope: "row", text: k }), td(P[k])]); }));
    }
    if (m.id === "CP-0" || m.id === "CP-5") {
      return kvTable(m.id + " counts", [kvRow("Cited figures", el("span", { class: "num", text: String(D.counts.cited) })), kvRow("Calculations", el("span", { class: "num", text: String(D.counts.calculated) })),
        kvRow("Gaps logged at Approval", el("span", { class: "num", text: String(D.limitations.length) })), kvRow("Modules not Pass", el("span", { class: "num", text: String(D.modules.filter(function (x) { return x.status !== "Pass"; }).length) }))]);
    }
    if (!list) return null;
    return kvTable(m.id + " key figures", list.map(function (f) { return el("tr", {}, [el("th", { scope: "row", text: f[1] }), td(fig(f[0]), f[2])]); }));
  }
  function moduleView(m) {
    var v = MODULE_VIEW[m.id] || { lead: null, detail: null };
    if (m.id === "CP-6") {
      v = /portfolio/i.test(m.name)
        ? { lead: ["bullet", "cloLimits"], detail: function () { return [el("p", { class: "prose" }, [judged(D.portfolio.fit.summary, [], true), txt(" "), el("a", { href: "#portfolio-fit", text: "Portfolio Fit" })])]; } }
        : { lead: ["riskMatrix", "risk"], detail: function () { return [el("ul", { class: "sw-list" }, I.weaknesses.map(function (w) { return el("li", {}, [el("b", { text: w.label }), el("span", {}, [judged(w.text, w.refs)])]); }))]; } };
    }
    return v;
  }
  function buildModules() {
    var host = $("mods"), counts = {};
    D.modules.forEach(function (m) { counts[m.status] = (counts[m.status] || 0) + 1; });
    $("analysis-meta").textContent = Object.keys(counts).map(function (k) { return counts[k] + " " + k; }).join(", ");
    D.modules.forEach(function (m) {
      var id = m.id.toLowerCase();
      var v = moduleView(m);
      var finding = el("p", { class: "mod__finding" }, [txt(m.reason + " ")].concat(chips(m.refs)));
      var lead = el("div", { class: "mod__lead" + (v.lead ? "" : " mod__lead--solo") }, [el("div", {}, [finding, moduleFigs(m)])]);
      if (v.lead) lead.appendChild(chartInto(v.lead[0], D.charts[v.lead[1]], "c-" + id + "-lead"));
      var det = el("details", { class: "xp xp--light", id: id + "-detail" }, [el("summary", { text: "Detail: " + m.id + " " + m.name })]);
      var body = el("div", { class: "xp__body" });
      var kids = v.detail ? v.detail() : [];
      if (!kids.length) kids = [el("p", { class: "note", text: "No further detail in this pack beyond the finding above." })];
      kids.forEach(function (k) { body.appendChild(k); });
      det.appendChild(body);
      host.appendChild(el("article", { class: "mod", id: id, "aria-labelledby": id + "-h" }, [
        el("div", { class: "mod__head" }, [el("span", { class: "mod__id", text: m.id }), el("h3", { id: id + "-h", text: m.name }), el("span", { class: "on-navy" }, [UI.status(m.status)])]),
        lead, det]));
    });
  }

  /* ================================================================ Model */
  function modelGrid(caption, groups) {
    var t = el("table", { class: "dt model-grid" });
    t.appendChild(el("caption", { class: "vh", text: caption }));
    t.appendChild(el("thead", {}, [el("tr", {}, [el("th", { scope: "col", text: "US$ m" })].concat(STOPS.map(function (s) {
      return el("th", { scope: "col", class: "num", "data-stops": s.id }, [s.label, el("small", { text: s.sub })]);
    })))]));
    var b = el("tbody");
    groups.forEach(function (g) {
      if (g.title) b.appendChild(el("tr", { class: "group" }, [el("th", { scope: "rowgroup", colspan: STOPS.length + 1, text: g.title })]));
      g.rows.forEach(function (r) {
        b.appendChild(el("tr", { class: r.cls || null }, [el("th", { scope: "row", text: r.label })].concat(STOPS.map(function (s) {
          var d = r.get(s), c = td(d, r.unit, { "data-stops": s.id });
          if (d && d.projected && !util.isGap(d)) c.appendChild(el("span", { class: "cell-proj", text: "proj." }));
          return c;
        }))));
      });
    });
    t.appendChild(b);
    return el("div", { class: "table-scroll" }, [t]);
  }
  function finRowSpec(r) { return { label: r.label, unit: /^%/.test(r.label) ? "%" : null, cls: r.kind === "sub" ? "sub" : r.kind === "total" ? "total" : null, get: function (s) { return finCell(r, s); } }; }
  function band(title, lede, kids, open) {
    var d = el("details", { class: "xp", id: "band-" + title.toLowerCase().replace(/[^a-z]+/g, "-").replace(/-$/, "") }, [el("summary", { text: title })]);
    if (open) d.open = true;
    d.appendChild(el("div", { class: "xp__body" }, [el("p", { class: "note", style: "margin-top:0", text: lede })].concat(kids)));
    return d;
  }
  function buildModel() {
    var strip = $("model-strip");
    strip.appendChild(el("p", { class: "note", style: "margin:0 0 var(--s-3)", text: "Model chart strip: leverage, interest cover and liquidity across the periods the sources carry. Open a band for its rows; click any cell for its source, locator and excerpt, or its formula." }));
    var cs = el("div", { class: "chart-strip" });
    ["leverage", "coverage", "liquidity"].forEach(function (k) { var h = el("div"); cs.appendChild(h); C.lineStrip(h, Object.assign({}, D.charts[k], { id: "c-model-" + k, headingLevel: 3, height: 180 })); });
    strip.appendChild(cs);
    var bands = $("bands");
    var fr = T.financials.rows;
    var cfStart = fr.findIndex ? fr.findIndex(function (r) { return /^Cash Interest/.test(r.label); }) : 6;
    bands.appendChild(band("Earnings", "Net revenues and company-defined Adjusted EBITDA by stop. Pro forma and projected stops are n/a with their reasons.", [modelGrid("Earnings", [{ rows: fr.slice(0, cfStart).map(finRowSpec) }])]));
    bands.appendChild(band("Adjusted EBITDA bridge", "Reported to Structuring to SSIM EBITDA, then the Q2 2026 reconciliation from net loss.", [periodTable(T.ebitdaAdjustments, "EBITDA adjustments"), chartInto("waterfall", D.charts.ebitdaBridge, "c-model-bridge")]));
    bands.appendChild(band("Cash flow waterfall", "FFO to FCF by stop; the 10-Q's interest estimates fill the first two projected years and are marked projected.", [
      modelGrid("Cash flow", [{ rows: fr.slice(cfStart).map(finRowSpec) }]),
      el("div", { class: "grid2" }, [chartInto("waterfall", D.charts.cashBridge, "c-model-cash"), chartInto("waterfall", liquiditySpec(), "c-model-liq")])]));
    var rankRows = function (rank) { return T.capitalStructure.rows.filter(function (r) { return r.rank === rank; }); };
    var stack = el("table", { class: "dt" });
    stack.appendChild(el("caption", { class: "vh", text: "Debt stack by rank" }));
    stack.appendChild(head([{ t: "Facility", text: true }, { t: "Rank", text: true }, { t: "Outstanding | US$ m", num: true }, { t: "Book | US$ m", num: true }, { t: "Cumulative multiple | x", num: true }, { t: "% EV", num: true }]));
    var sb = el("tbody");
    [["secured", "Senior secured", "senior_secured"], ["unsecured", "Unsecured", "unsecured"], ["other", "Other", "other"]].forEach(function (g) {
      sb.appendChild(el("tr", { class: "group" }, [el("th", { scope: "rowgroup", colspan: 6, text: g[1] })]));
      rankRows(g[0]).forEach(function (r) { sb.appendChild(el("tr", { class: "indent" }, [el("th", { scope: "row", text: r.facility }), el("td", { text: r.debtType }), td(r.outstanding), td(r.book), td(r.structuring_multiple), td(r.pct_ev)])); });
      sb.appendChild(el("tr", { class: "total" }, [el("th", { scope: "row", colspan: 2, text: g[1] + " total" }), td(T.capitalStructure.subtotals[g[2]]), el("td"), el("td"), el("td")]));
    });
    stack.appendChild(sb);
    var mat = el("table", { class: "dt" });
    mat.appendChild(el("caption", { class: "vh", text: T.maturities.title }));
    mat.appendChild(head([{ t: "Year", text: true }, { t: "Due | US$ m", num: true }]));
    mat.appendChild(el("tbody", {}, T.maturities.rows.map(function (r) { return el("tr", {}, [el("th", { scope: "row", text: r.label }), td(r.cell)]); })));
    bands.appendChild(band("Debt stack by rank", "Face value at 30 June 2026 by rank, cumulative multiple of LTM Adjusted EBITDA and share of the merger's EV; annual maturities from the 10-Q.", [
      el("div", { class: "grid2" }, [el("div", { class: "table-scroll" }, [stack]), el("div", {}, [el("p", { class: "subhead", text: T.maturities.title }), mat])]),
      chartInto("columns", stackSpec(), "c-model-stack")]));
    bands.appendChild(band("Credit metrics", "Balance sheet and credit metrics by stop. Leverage is an LTM measure; interim stops carry cover only.", [modelGrid("Credit metrics", [
      { title: "Balance sheet, period end", rows: T.balanceSheet.rows.map(function (r) { return { label: r.label, get: function (s) { return bsCell(r, s); } }; }) },
      { title: "Credit metrics, x", rows: T.creditMetrics.rows.map(function (r) { return { label: r.label, unit: "x", get: function (s) { return cmCell(r, s); } }; }) }])]));
  }

  /* ================================================================ Portfolio Fit */
  function buildFit() {
    var P = D.portfolio, fit = P.fit, host = $("pfit");
    $("pf-meta").textContent = P.name + ", " + P.asOf + "; synthetic portfolio";
    host.appendChild(el("div", { class: "sec__lede" }, [el("p", {}, [el("span", { class: "synth", text: "Synthetic" }), txt(" Test CLO I is a synthetic portfolio built for testing; its files are cited as S refs. The fit verdict is "), UI.illus(), txt(" because no RBOT run exists.")])]));
    var checks = el("table", { class: "dt" });
    checks.appendChild(el("caption", { class: "vh", text: "Portfolio Fit checks" }));
    checks.appendChild(head([{ t: "Constraint", text: true }, { t: "Limit", text: true }, { t: "Current", num: true }, { t: "Headroom", num: true }, { t: "Result", text: true }, { t: "Note", text: true }]));
    checks.appendChild(el("tbody", {}, fit.checks.map(function (c) {
      return el("tr", {}, [el("th", { scope: "row", text: c.constraint }), el("td", { text: c.limit }), td({ v: c.current, prov: "synthetic", ref: c.ref }), td({ v: c.headroom, prov: "synthetic", ref: c.ref }),
        el("td", {}, [UI.status(c.result)]), el("td", { class: "excerpt", text: c.note || "" })]);
    })));
    var inst = el("table", { class: "dt" });
    inst.appendChild(el("caption", { class: "vh", text: "Portfolio Fit by instrument" }));
    inst.appendChild(head([{ t: "Instrument", text: true }, { t: "Fit", text: true }, { t: "Why", text: true }]));
    inst.appendChild(el("tbody", {}, fit.byInstrument.map(function (r) { return el("tr", {}, [el("th", { scope: "row", text: r.instrument }), el("td", {}, [UI.status(r.fit), UI.illus()]), el("td", { text: r.note || "" })]); })));
    var left = el("section", { class: "block" }, [bar("h3", "Fit for " + P.name, null, frag([txt(" "), el("span", { class: "on-navy" }, [UI.status(fit.overall.v), UI.illus()])])),
      el("div", { class: "block__body" }, [el("p", { class: "prose" }, [judged(fit.summary, [], false)])]),
      el("div", { class: "table-scroll" }, [checks]), el("div", { class: "table-scroll" }, [inst])]);
    var right = el("section", { class: "block" }, [bar("h3", "Limits and sector weights", "synthetic"), el("div", { class: "block__body" }, [chartInto("bullet", D.charts.cloLimits, "c-fit-limits"), chartInto("rangeStrip", D.charts.cloSectors, "c-fit-sectors")])]);
    host.appendChild(el("div", { class: "snap" }, [left, right]));
    var sumRows = Object.keys(P.summary).map(function (k) { return el("tr", {}, [el("th", { scope: "row", text: k }), td(P.summary[k])]); });
    var manRows = Object.keys(P.mandate).map(function (k) { return el("tr", {}, [el("th", { scope: "row", text: k }), tdText(P.mandate[k])]); });
    var con = el("table", { class: "dt" });
    con.appendChild(el("caption", { class: "vh", text: "Constraints compliance monitor" }));
    con.appendChild(head([{ t: "ID", text: true }, { t: "Category", text: true }, { t: "Parameter", text: true }, { t: "Limit", text: true }, { t: "Type", text: true }, { t: "Current", num: true }, { t: "Headroom", num: true }, { t: "Status", text: true }]));
    con.appendChild(el("tbody", {}, P.constraints.map(function (c) {
      return el("tr", {}, [el("th", { scope: "row", text: c.id }), el("td", { text: c.category }), el("td", { text: c.parameter }), el("td", { text: c.limit }), el("td", { text: c.breachType }), td({ v: c.current, prov: "synthetic", ref: c.ref }), td({ v: c.headroom, prov: "synthetic", ref: c.ref }), el("td", {}, [UI.status(c.status === "Pass" ? "Pass" : c.status)])]);
    })));
    var det = el("details", { class: "xp", id: "fit-detail" }, [el("summary", { text: "Test CLO I portfolio, mandate and constraints" }), el("div", { class: "xp__body" }, [
      el("div", { class: "grid2" }, [kvTable("Portfolio summary", sumRows), kvTable("Mandate", manRows)]), el("div", { class: "table-scroll" }, [con])])]);
    host.appendChild(el("div", { style: "margin-top:var(--s-4)" }, [det]));
  }

  /* ================================================================ Evidence */
  function buildEvidence() {
    var host = $("evid"), K = D.counts;
    $("ev-meta").textContent = K.cited + " cited, " + K.calculated + " calculated, " + K.gaps + " gaps, " + K.synthetic_sources + " synthetic";
    var cites = Object.keys(D.citations).map(function (k) { return D.citations[k]; });
    var real = cites.filter(function (c) { return !c.synthetic; }), synth = cites.filter(function (c) { return c.synthetic; });
    function tbl(caption, cols, rows) {
      var t = el("table", { class: "dt" });
      t.appendChild(el("caption", { class: "vh", text: caption }));
      t.appendChild(head(cols.map(function (c) { return { t: c, text: true }; })));
      t.appendChild(el("tbody", {}, rows));
      return el("div", { class: "ev-table" }, [t]);
    }
    function row(text, cells) { return el("tr", { "data-text": text.toLowerCase() }, cells); }
    var panels = [
      { key: "cited", label: "Cited", n: real.length, build: function () { return tbl("Cited figures", ["Ref", "Figure", "Period", "Value", "File and locator", "Excerpt"], real.map(function (c) {
        return row([c.id, c.label, c.period, c.value, c.file, c.excerpt].join(" "), [el("th", { scope: "row" }, [UI.chip(c.id)]), el("td", { text: c.label }), el("td", { text: c.period || "" }), el("td", { class: "num", text: c.value }), el("td", { text: c.file + ", " + c.locator }), el("td", { class: "excerpt", text: c.excerpt || "" })]);
      })); } },
      { key: "calc", label: "Calculated", n: Object.keys(D.calcs).length, build: function () { return tbl("Calculations", ["Ref", "Figure", "Period", "Value", "Formula", "Inputs"], Object.keys(D.calcs).map(function (k) {
        var c = D.calcs[k];
        return row([c.id, c.label, c.period, c.value, c.formula].join(" "), [el("th", { scope: "row" }, [UI.chip(c.id)]), el("td", { text: c.label }), el("td", { text: c.period || "" }), el("td", { class: "num", text: c.value }), el("td", {}, [el("code", { text: c.formula })]), el("td", {}, chips(c.inputs))]);
      })); } },
      { key: "gaps", label: "Gaps", n: Object.keys(D.gaps).length, build: function () { return tbl("Gaps", ["Ref", "Field", "Reason", "Origin"], Object.keys(D.gaps).map(function (k) {
        var g = D.gaps[k];
        return row([g.id, g.field, g.reason].join(" "), [el("th", { scope: "row" }, [UI.chip(g.id)]), el("td", { text: g.field }), el("td", { class: "excerpt", text: g.reason }), el("td", { text: g.origin })]);
      })); } },
      { key: "synth", label: "Synthetic", n: synth.length, build: function () { return tbl("Synthetic portfolio rows", ["Ref", "File and locator", "Excerpt"], synth.map(function (c) {
        return row([c.id, c.file, c.excerpt].join(" "), [el("th", { scope: "row" }, [UI.chip(c.id)]), el("td", { text: c.file + ", " + c.locator }), el("td", { class: "excerpt", text: c.excerpt || "" })]);
      })); } }
    ];
    var input = el("input", { type: "search", id: "ev-q", placeholder: "Filter by ref, figure, file or excerpt", autocomplete: "off" });
    var count = el("span", { class: "ev-count", role: "status" });
    var tabs = el("div", { "data-tabs": "" });
    var list = el("div", { class: "tabs__list", "aria-label": "Evidence by origin" });
    tabs.appendChild(list);
    panels.forEach(function (p, i) {
      list.appendChild(el("button", { type: "button", class: "tabs__tab", id: "evt-" + p.key, "aria-controls": "evp-" + p.key, "aria-selected": i === 0 ? "true" : "false", text: p.label + " (" + p.n + ")" }));
      tabs.appendChild(el("div", { class: "tabs__panel", id: "evp-" + p.key, hidden: i !== 0 }, [p.build()]));
    });
    function filter() {
      var q = input.value.trim().toLowerCase(), shown = 0, total = 0;
      tabs.querySelectorAll("tr[data-text]").forEach(function (r) { total++; var on = !q || r.getAttribute("data-text").indexOf(q) >= 0; r.hidden = !on; if (on) shown++; });
      count.textContent = q ? shown + " of " + total + " records match" : total + " records";
    }
    input.addEventListener("input", filter);
    var det = el("details", { class: "xp", id: "evidence-register" }, [el("summary", { text: "Evidence register: every citation with its excerpt, every formula with its inputs" }),
      el("div", { class: "xp__body" }, [el("div", { class: "ev-tools" }, [el("label", { for: "ev-q", text: "Filter" }), input, count]), tabs])]);
    host.appendChild(el("div", { class: "sec__lede" }, [el("p", { text: "Every figure in this Report is cited to a line of a filing in the Source Pack, calculated by a script from cited inputs, or logged as a gap. Open the register to search all of them." })]));
    host.appendChild(el("div", { style: "margin-top:var(--s-3)" }, [det]));
    filter();
  }

  /* ================================================================ Limitations */
  function limitationsTable(list, caption) {
    var t = el("table", { class: "dt" });
    t.appendChild(el("caption", { class: "vh", text: caption }));
    t.appendChild(head([{ t: "Gap", text: true }, { t: "Field", text: true }, { t: "What is missing", text: true }, { t: "Scope", text: true }, { t: "Origin", text: true }]));
    t.appendChild(el("tbody", {}, list.map(function (l) { return el("tr", {}, [el("th", { scope: "row" }, [UI.chip(l.ref)]), el("td", { class: "field", text: l.field }), el("td", { class: "excerpt", text: l.text }), el("td", { text: l.scope }), el("td", { text: l.origin })]); })));
    return el("div", { class: "table-scroll" }, [t]);
  }
  function buildLimitations() {
    var host = $("lims"), L = D.limitations;
    var model = L.filter(function (l) { return /model limitation/i.test(l.scope); }), pack = L.filter(function (l) { return !/model limitation/i.test(l.scope); });
    $("lim-meta").textContent = L.length + " known at Approval; none unforeseen";
    var restricted = D.modules.filter(function (m) { return m.status !== "Pass"; });
    host.appendChild(el("div", { class: "sec__lede" }, [el("p", { text: "Known at Approval: every gap in the Source Pack and every module restriction, stated before the run. Unforeseen: anything that arose during the run." })]));
    host.appendChild(el("div", { class: "snap" }, [
      block("lim-modules", "Module restrictions at Approval", restricted.length + " of " + D.modules.length + " modules", [el("ul", { class: "sw-list" }, restricted.map(function (m) {
        return el("li", {}, [el("span", {}, [el("b", { text: m.id + " " }), UI.status(m.status)]), el("span", {}, [txt(m.reason + " ")].concat(chips(m.refs)))]);
      }))]),
      block("lim-model", "Model limitations at Approval", model.length + " items", [limitationsTable(model, "Model limitations"),
        el("div", { class: "block__body" }, [el("p", { class: "subhead", text: "Unforeseen during the run" }), el("p", { class: "prose", text: "None recorded. No RBOT run exists, so no limitation arose after Approval." })])]),
      block("lim-pack", "Source Pack gaps at Approval", pack.length + " items", [limitationsTable(pack, "Source Pack gaps")], "span-2")
    ]));
    $("foot").appendChild(el("p", { text: "RBOT Report mockup, direction C (period spine). " + D.meta.runNote + " Caesars figures are cited from public filings and FINRA TRACE; every score, recommendation, valuation and thesis line is illustrative; Test CLO I is synthetic." }));
  }

  /* ================================================================ navigation: where am I, deep links, print */
  function wireNav() {
    var links = Array.prototype.slice.call(document.querySelectorAll("#nav-list a"));
    var map = {}; links.forEach(function (a) { map[a.getAttribute("href").slice(1)] = a; });
    var ids = Object.keys(map), current = null;
    function setCurrent(id) {
      if (id === current) return; current = id;
      links.forEach(function (a) { if (a === map[id]) a.setAttribute("aria-current", "true"); else a.removeAttribute("aria-current"); });
      var a = map[id]; if (a && a.scrollIntoView && window.innerWidth < 760) { var ol = a.closest("ol"); ol.scrollLeft = a.offsetLeft - 16; }
    }
    function onScroll() {
      var y = (document.querySelector(".nav").getBoundingClientRect().bottom || 0) + 24, pick = ids[0];
      ids.forEach(function (id) { var n = $(id); if (n && n.getBoundingClientRect().top <= y) pick = id; });
      var de = document.documentElement;
      if (de.scrollHeight > window.innerHeight + 8 && window.innerHeight + window.scrollY >= de.scrollHeight - 4) pick = ids[ids.length - 1];
      setCurrent(pick);
    }
    window.addEventListener("scroll", onScroll, { passive: true });
    onScroll();
    function openTarget() {
      var id = decodeURIComponent(location.hash.slice(1)); if (!id) return;
      var n = $(id); if (!n) return;
      var d = n.tagName === "DETAILS" ? n : n.closest("details");
      if (d) d.open = true;
      var inner = n.querySelector && n.querySelector(":scope > details");
      if (inner && n.classList.contains("mod")) inner.open = true;
      requestAnimationFrame(function () { n.scrollIntoView({ block: "start" }); });
    }
    window.addEventListener("hashchange", openTarget);
    openTarget();
    var reopened = [];
    window.addEventListener("beforeprint", function () { forPrint(true); reopened = Array.prototype.slice.call(document.querySelectorAll("details:not([open])")); reopened.forEach(function (d) { d.open = true; }); });
    window.addEventListener("afterprint", function () { forPrint(false); reopened.forEach(function (d) { d.open = false; }); reopened = []; });
  }

  /* ================================================================ build */
  buildMast();
  buildVerdict();
  buildSpine();
  buildSnapshot();
  buildModules();
  buildModel();
  buildFit();
  buildEvidence();
  buildLimitations();
  UI.init(document);
  select(sel);
  wireNav();

  var ds = location.search.match(/[?&]demo=stop-([a-z0-9-]+)/);
  if (ds && STOP_IX[ds[1]] !== undefined) select(STOP_IX[ds[1]]);
  /* ?demo=expanded: two sections open and one citation popover, for review screenshots */
  if (/[?&]demo=expanded\b/.test(location.search)) {
    var mods = document.querySelectorAll(".mod"), m1 = $("cp-1") || mods[1] || mods[0], m2 = m1 && m1.nextElementSibling;
    [m1, m2].forEach(function (m) { if (m) { var d = m.querySelector("details"); if (d) d.open = true; } });
    if (m1) {
      m1.scrollIntoView({ block: "start" });
      document.documentElement.setAttribute("data-demo-y", String(Math.round(m1.getBoundingClientRect().top + window.scrollY)));
      var chip = m1.querySelector('.mod__lead .cellref[data-ref^="C"]') || m1.querySelector("button[data-ref]");
      if (chip) UI.open(chip.getAttribute("data-ref"), chip);
    }
  }
  document.documentElement.setAttribute("data-ready", "1");
})();
