/* RBOT Report, direction B: verdict rail. Builds the page from window.RBOT_DATA with the shared
   RBOTUI / RBOTCharts kit. Every value is a Datum {v, prov, ref, reason} printed exactly as served.
   Module statuses and limitations are read from RBOT_DATA at run time, never written here.
   Adds two things the shared kit lacks: a debt-stack chart (capital structure by cumulative
   multiple) and an n/a chart frame for a chart the Source Pack cannot draw. */
(function () {
  "use strict";

  var D = window.RBOT_DATA, UI = window.RBOTUI, C = window.RBOTCharts, el = UI.el;
  var F = D.figures, I = D.illustrative, T = D.tables, K = D.charts;
  var U = C.util;
  function $(id) { return document.getElementById(id); }
  function tx(s) { return document.createTextNode(s); }
  function frag(kids) { var f = document.createDocumentFragment(); kids.forEach(function (k) { if (k) f.appendChild(typeof k === "string" ? tx(k) : k); }); return f; }

  /* ------------------------------------------------------------ data helpers */
  function fig(k) {
    var f = F[k];
    if (!f) return pageGap(k, "not in the sources");
    return { v: f.v, prov: f.prov, ref: f.ref, reason: f.reason };
  }
  function gapDatum(ref) { var g = D.gaps[ref]; return { v: null, prov: "gap", ref: ref, reason: g ? g.reason : "not in the sources" }; }
  /* A gap the page draws that has no G record: kept as a page-level limitation (shown under Limitations, Unforeseen). */
  var PAGE_GAPS = [], PAGE_GAP_SEEN = {};
  function pageGap(field, reason, where) {
    if (!PAGE_GAP_SEEN[field]) { PAGE_GAP_SEEN[field] = true; PAGE_GAPS.push({ field: field, reason: reason, where: where || "" }); }
    return { v: null, prov: "gap", reason: reason };
  }
  function chips(refs) { return frag((refs || []).map(function (r) { return UI.chip(r); })); }
  function value(d, unit) { return UI.value(d, unit); }
  function modelText(text, refs, illus) {
    return frag([el("span", { class: "prov-model", text: text }), chips(refs), illus === false ? null : UI.illus()]);
  }
  function dirClass(word) {
    var w = String(word || "").toLowerCase();
    return (w === "improving" || w === "positive") ? "dir dir--up" : (w === "deteriorating" || w === "negative") ? "dir dir--down" : "dir dir--flat";
  }
  function slug(id) { return String(id).toLowerCase().replace(/[^a-z0-9]+/g, "-"); }
  function short(n) { return n.replace(/^CEI /, ""); }

  /* ------------------------------------------------------------ table helpers */
  function td(d, opts) {
    opts = opts || {};
    var c = el("td", { class: opts.text ? "txt" : "num" });
    UI.cell(c, d, opts.unit);
    return c;
  }
  function kv(tbody, label, kids) { tbody.appendChild(el("tr", {}, [el("th", { scope: "row", text: label }), el("td", {}, kids)])); }
  function kvTable(caption) {
    var t = el("table", { class: "dt dt--kv" }, [el("caption", { class: "vh", text: caption })]);
    var b = el("tbody"); t.appendChild(b);
    return { table: t, body: b };
  }
  function head(cols) {
    return el("thead", {}, [el("tr", {}, cols.map(function (hd, i) {
      var txt = String(hd).charAt(0) === "~", p = String(hd).replace(/^~/, "").split(" | ");
      return el("th", { scope: "col", class: (i > 0 && !txt) ? "num" : null }, [p[0], p[1] ? el("span", { class: "unit", text: p[1] }) : null]);
    }))]);
  }
  function scroll(t) { return el("div", { class: "table-scroll" }, [t]); }
  function periodGrid(t, opts) {
    opts = opts || {};
    var tt = el("table", { class: "dt dt--framed" + (opts.wrap ? " dt--wrap" : "") }, [el("caption", { class: "vh", text: t.title })]);
    tt.appendChild(head([t.unit].concat(t.columns)));
    var b = el("tbody"); tt.appendChild(b);
    t.rows.forEach(function (r) {
      if (opts.filter && !opts.filter(r)) return;
      var row = el("tr", { class: r.kind === "total" ? "total" : r.kind === "sub" ? "sub" : r.kind === "indent" ? "indent" : null }, [el("th", { scope: "row", text: r.label })]);
      r.cells.forEach(function (d) { row.appendChild(td(d, { unit: opts.unit })); });
      b.appendChild(row);
    });
    return scroll(tt);
  }
  function listTable(caption, cols, rows) {
    var t = el("table", { class: "dt dt--framed" }, [el("caption", { class: "vh", text: caption }), head(cols)]);
    var b = el("tbody"); t.appendChild(b);
    rows.forEach(function (r) { b.appendChild(r); });
    return scroll(t);
  }

  /* ------------------------------------------------------------ cards and charts */
  function card(id, title, opts, kids) {
    opts = opts || {};
    var bar = el("h3", { class: "bar" }, [el("span", { text: title }), opts.meta ? el("span", { class: "bar__meta" }, opts.meta) : null]);
    var body = el("div", { class: "card__body" }, kids);
    return el("section", { class: "block card " + (opts.span || "span-12"), id: id, "aria-labelledby": id + "-h" }, [set(bar, id + "-h"), body]);
  }
  function set(node, id) { node.id = id; return node; }
  function more(label, kids, open) {
    var d = el("details", { class: "xp xp--light" }, [el("summary", {}, [el("span", { class: "xp__label", text: label })]), el("div", { class: "xp__body" }, kids)]);
    if (open) d.open = true;
    return d;
  }
  function chartHost(cls) { return el("div", { class: "chart-host " + (cls || "") }); }
  var DRAWN = [];
  function draw(kind, host, base, extra) {
    var s = Object.assign({}, base, { headingLevel: 4 }, extra || {});
    DRAWN.push(function () { C[kind](host, s); });
    return host;
  }

  /* Debt stack: one floating bar per facility from the previous cumulative multiple to its own,
     coloured by rank, with the secured and total subtotals and EV at the merger value as rules.
     Floats only place marks; every printed figure is the served string. */
  var SVGNS = "http://www.w3.org/2000/svg";
  function sv(tag, attrs, kids) {
    var n = document.createElementNS(SVGNS, tag);
    Object.keys(attrs || {}).forEach(function (k) { if (attrs[k] !== null && attrs[k] !== undefined) n.setAttribute(k, attrs[k]); });
    (kids || []).forEach(function (c) { if (c) n.appendChild(c); });
    return n;
  }
  function svText(x, y, t, attrs) { var n = sv("text", Object.assign({ x: x, y: y }, attrs || {})); n.textContent = t; return n; }
  var ctx2d = null;
  function textW(t, size, weight) {
    if (!ctx2d) ctx2d = document.createElement("canvas").getContext("2d");
    ctx2d.font = (weight || 400) + " " + (size || 11) + "px Inter, system-ui, sans-serif";
    return ctx2d.measureText(String(t)).width;
  }
  function fit(t, w, size, weight) {
    if (textW(t, size, weight) <= w) return t;
    while (t.length > 3 && textW(t + "…", size, weight) > w) t = t.slice(0, -1);
    return t + "…";
  }
  function cssVar(name) { return getComputedStyle(document.documentElement).getPropertyValue(name).trim(); }
  function frame(host, o) {
    while (host.firstChild) host.removeChild(host.firstChild);
    var tid = o.id + "-twin";
    var plot = el("div", { class: "chart__plot" });
    var tip = el("div", { class: "chart__tip", role: "status", hidden: true });
    var legend = el("ul", { class: "chart__legend", "aria-label": "Legend" });
    var toggle = el("button", { type: "button", class: "btn btn--quiet chart__toggle", "aria-expanded": "false", "aria-controls": tid, text: "Show table" });
    var twin = el("div", { class: "chart__twin", id: tid, hidden: true });
    toggle.addEventListener("click", function () {
      var openNow = toggle.getAttribute("aria-expanded") !== "true";
      toggle.setAttribute("aria-expanded", String(openNow)); toggle.textContent = openNow ? "Hide table" : "Show table"; twin.hidden = !openNow;
    });
    var f = el("figure", { class: "chart chart--" + o.kind, id: o.id, "data-chart": o.kind }, [
      el("div", { class: "chart__head" }, [el("h4", { class: "chart__title", text: o.title }), o.summary ? el("p", { class: "chart__summary", text: o.summary }) : null]),
      plot,
      o.noFoot ? null : el("div", { class: "chart__foot" }, [legend, o.twin ? toggle : null]),
      o.twin ? twin : null,
      o.source ? el("p", { class: "chart__source", text: "Source: " + o.source }) : null
    ]);
    host.appendChild(f);
    return { plot: plot, tip: tip, legend: legend, twin: twin };
  }
  function legendItem(kind, color, label) {
    var s = sv("svg", { width: 22, height: 12, viewBox: "0 0 22 12", "aria-hidden": "true" });
    if (kind === "rule") s.appendChild(sv("line", { x1: 11, x2: 11, y1: 0, y2: 12, stroke: color, "stroke-width": 2 }));
    else if (kind === "dashrule") s.appendChild(sv("line", { x1: 11, x2: 11, y1: 0, y2: 12, stroke: color, "stroke-width": 2, "stroke-dasharray": "3 2" }));
    else s.appendChild(sv("rect", { x: 3, y: 1, width: 16, height: 10, fill: color }));
    return el("li", {}, [s, label]);
  }
  function svgMark(svg, tip, plot, box, label, ref, kids) {
    var g = sv("g", { class: "mark", tabindex: 0, role: "img", "aria-label": label, "data-ref": ref || null }, kids);
    var w = Math.max(24, box.w), h = Math.max(24, box.h);
    g.appendChild(sv("rect", { class: "hit", x: box.x + box.w / 2 - w / 2, y: box.y + box.h / 2 - h / 2, width: w, height: h, rx: 2 }));
    function show() {
      tip.textContent = label + (ref ? ". Press Enter or click for the source." : ""); tip.hidden = false;
      var pr = plot.getBoundingClientRect(), mr = g.getBoundingClientRect(), tw = Math.min(288, tip.offsetWidth || 200);
      tip.style.left = Math.min(Math.max(0, mr.left - pr.left + mr.width / 2 - tw / 2), pr.width - tw) + "px";
      var top = mr.top - pr.top - (tip.offsetHeight || 40) - 6;
      tip.style.top = (top < -10 ? mr.bottom - pr.top + 6 : top) + "px";
    }
    function hide() { tip.hidden = true; }
    function press(e) { if (ref) { UI.open(ref, g); hide(); } else show(); if (e) e.preventDefault(); }
    g.addEventListener("mouseenter", show); g.addEventListener("mouseleave", hide);
    g.addEventListener("focus", show); g.addEventListener("blur", hide);
    g.addEventListener("click", press);
    g.addEventListener("keydown", function (e) { if (e.key === "Enter" || e.key === " ") press(e); if (e.key === "Escape") hide(); });
    svg.appendChild(g);
    return g;
  }

  function debtStack(host) {
    var cap = T.capitalStructure, sub = cap.subtotals, rows = cap.rows;
    var recs = {}; I.byInstrument.forEach(function (r) { recs[r.facility] = r; });
    var secured = rows.filter(function (r) { return r.rank === "secured"; });
    var lastSec = secured[secured.length - 1], lastRow = rows[rows.length - 1];
    var summary = "Secured " + lastSec.structuring_multiple.v + "x, total " + lastRow.structuring_multiple.v + "x; EV " + sub.ev_multiple.v + "x at the merger value.";
    var fr = frame(host, { id: "fig-debt-stack", kind: "debtStack", title: "Debt stack by rank, cumulative multiple", summary: summary, twin: true });
    var rankColor = { secured: cssVar("--chart-1") || "#0017E5", unsecured: cssVar("--chart-2") || "#C4410C", other: cssVar("--chart-neutral") || "#8D939D" };
    var rankWord = { secured: "Senior secured", unsecured: "Unsecured", other: "Other" };
    ["secured", "unsecured", "other"].forEach(function (k) { fr.legend.appendChild(legendItem("fill", rankColor[k], k === "secured" ? "Secured" : rankWord[k])); });
    fr.legend.appendChild(legendItem("rule", cssVar("--navy") || "#000533", "Subtotal"));
    fr.legend.appendChild(legendItem("dashrule", cssVar("--chart-axis") || "#55585E", "EV"));
    /* twin: the facility rows as served */
    var trs = rows.map(function (r) {
      var rec = recs[r.facility];
      return el("tr", {}, [el("th", { scope: "row", text: r.facility }), el("td", { text: rankWord[r.rank] }), td(r.outstanding), td(r.structuring_multiple, { unit: "x" }), td(r.pct_ev),
        el("td", {}, [rec ? UI.scale({ kind: "rec", pos: rec.pos, word: rec.word, illustrative: true, label: r.facility }) : ""])]);
    });
    fr.twin.appendChild(el("p", { class: "chart__source", text: "Source: Caesars Q2 2026 10-Q debt table; multiples and % EV by build-data.py on LTM Adjusted EBITDA " + F.ltm_adj_ebitda_q2_2026.v + "." }));
    fr.twin.insertBefore(listTable("Debt stack, table", ["Facility", "~Rank", "Outstanding | US$ m", "Cumulative | x", "% EV | %", "~Recommendation | illustrative"], trs), fr.twin.firstChild);

    function render() {
      while (fr.plot.firstChild) fr.plot.removeChild(fr.plot.firstChild);
      var W = Math.max(300, Math.round(fr.plot.clientWidth || 600));
      var narrow = W < 460;
      var labW = Math.min(W * (narrow ? 0.36 : 0.34), 230), rowH = 15, left = labW + 6, right = W - 10;
      var hi = Math.max(U.parseNum(sub.ev_multiple.v), U.parseNum(lastRow.structuring_multiple.v));
      var maxT = Math.ceil(hi), x = function (v) { return left + v / maxT * (right - left); };
      /* subtotal rules: place their labels first (up to three lines), so the plot starts below them */
      var navy = cssVar("--navy") || "#000533", axis = cssVar("--chart-axis") || "#55585E";
      var rules = [
        { d: lastSec.structuring_multiple, text: "Secured " + lastSec.structuring_multiple.v + "x", dash: null, c: navy, name: "Senior secured debt " + sub.senior_secured.v + " US$ m, cumulative " + lastSec.structuring_multiple.v + "x" },
        { d: lastRow.structuring_multiple, text: "Total " + lastRow.structuring_multiple.v + "x", dash: null, c: navy, name: "Total debt " + sub.total_debt.v + " US$ m, " + lastRow.structuring_multiple.v + "x" },
        { d: sub.ev_multiple, text: "EV " + sub.ev_multiple.v + "x", dash: "4 3", c: axis, name: "EV at the merger's stated value " + sub.ev.v + " US$ m, " + sub.ev_multiple.v + "x" }
      ];
      var placedR = [], maxY = 11;
      rules.forEach(function (rl) {
        var rx = Math.round(x(U.parseNum(rl.d.v))) + 0.5, w = textW(rl.text, 10.5, 600), opts = [];
        [11, 24, 37].forEach(function (yy) { opts.push({ y: yy, a: "start", x0: rx + 4, x1: rx + 4 + w }); opts.push({ y: yy, a: "end", x0: rx - 4 - w, x1: rx - 4 }); });
        var pick = opts.filter(function (o) {
          return o.x1 <= W - 1 && o.x0 >= left && !placedR.some(function (p) { return p.y === o.y && o.x0 < p.x1 + 6 && o.x1 > p.x0 - 6; });
        })[0] || opts[1];
        placedR.push(pick); rl.rx = rx; rl.pick = pick; maxY = Math.max(maxY, pick.y);
      });
      var top = maxY + 12;
      var bottom = top + rows.length * rowH, H = bottom + 24;
      var svg = sv("svg", { role: "group", "aria-label": "Debt stack by rank, chart; each bar is focusable", viewBox: "0 0 " + W + " " + H, width: W, height: H });
      var ax = sv("g", { class: "grid ax", "aria-hidden": "true" });
      for (var t = 0; t <= maxT; t++) {
        var xx = Math.round(x(t)) + 0.5;
        ax.appendChild(sv("line", { x1: xx, x2: xx, y1: top - 4, y2: bottom }));
        ax.appendChild(svText(xx, bottom + 14, t + "x", { "text-anchor": "middle" }));
      }
      svg.appendChild(ax);
      var prev = 0;
      rows.forEach(function (r, i) {
        var cy = top + rowH * (i + 0.5);
        svg.appendChild(svText(labW, cy + 4, fit(short(r.facility), labW - 4, 11, 500), { "text-anchor": "end", class: "lbl--muted", "aria-hidden": "true" }));
        var b = U.parseNum(r.structuring_multiple.v), a = prev; prev = b;
        var x0 = x(a), x1 = x(b), bw = Math.max(2, x1 - x0);
        var lbl = r.outstanding.v + " · " + r.structuring_multiple.v + "x";
        var lw = textW(lbl, 10.5, 600), lx = x0 + bw + 5, anchor = "start";
        if (lx + lw > W - 2) { lx = x0 - 5; anchor = "end"; }
        var rec = recs[r.facility];
        var name = r.facility + " (" + rankWord[r.rank].toLowerCase() + "): " + r.outstanding.v + " US$ m outstanding (" + U.provWord(r.outstanding) + "), cumulative " +
          r.structuring_multiple.v + "x LTM Adjusted EBITDA (" + U.provWord(r.structuring_multiple) + "), " + r.pct_ev.v + "% of EV" + (rec ? ", recommendation " + rec.word + " (illustrative)" : "");
        svgMark(svg, fr.tip, fr.plot, { x: x0, y: cy - 6, w: bw, h: 12 }, name, r.structuring_multiple.ref, [
          sv("rect", { x: x0, y: cy - 5.5, width: bw, height: 11, fill: rankColor[r.rank] }),
          svText(lx, cy + 4, lbl, { class: "lbl", "text-anchor": anchor, style: "font-size:10.5px" })
        ]);
      });
      rules.forEach(function (rl) {
        var y = rl.pick.y, tx0 = rl.pick.a === "end" ? rl.rx - 4 : rl.rx + 4;
        svgMark(svg, fr.tip, fr.plot, { x: rl.rx - 2, y: y - 9, w: 4, h: bottom - y + 9 }, rl.name + " (" + U.provWord(rl.d) + ")", rl.d.ref, [
          sv("line", { x1: rl.rx, x2: rl.rx, y1: y + 3, y2: bottom, stroke: rl.c, "stroke-width": 1.5, "stroke-dasharray": rl.dash }),
          svText(tx0, y, rl.text, { class: "lbl", "text-anchor": rl.pick.a, style: "font-size:10.5px;fill:" + rl.c })
        ]);
      });
      fr.plot.appendChild(svg);
      fr.plot.appendChild(fr.tip);
    }
    DRAWN.push(function () {
      render();
      var last = fr.plot.clientWidth;
      if (typeof ResizeObserver === "function") new ResizeObserver(function () { if (Math.abs(fr.plot.clientWidth - last) > 2) { last = fr.plot.clientWidth; requestAnimationFrame(render); } }).observe(fr.plot);
      if (document.fonts && document.fonts.ready) document.fonts.ready.then(render);
    });
    return host;
  }

  /* n/a chart frame: the chart's title, what it would show, and the input it needs. */
  function naChart(host, o) {
    var fr = frame(host, { id: o.id, kind: "na", title: o.title, summary: o.summary, source: o.source, noFoot: true });
    fr.plot.appendChild(el("div", { class: "na-frame", role: "img", "aria-label": o.title + ": not drawn. " + o.needs }, [
      el("span", { class: "na-frame__big", text: "n/a" }),
      el("p", {}, [o.needs + " ", chips(o.refs)])
    ]));
    return host;
  }

  /* ================================================================ rail */
  var M = D.meta;
  (function rail() {
    var issuer = $("rail-issuer");
    issuer.appendChild(el("p", { class: "rail__issuer" }, [M.issuer + " ", UI.chip(M.issuerRef)]));
    issuer.appendChild(el("p", { class: "rail__sub", text: M.ticker + " · " + M.pathway + " · " + M.reportingPeriod }));
    if (M.primary) issuer.appendChild(el("span", { class: "rail__primary", text: M.primaryLabel }));

    $("rail-rec-illus").appendChild(UI.illus());
    var rec = $("rail-rec");
    M.strategies.forEach(function (s) {
      var r = I.recommendation[s];
      rec.appendChild(el("dt", { text: s }));
      rec.appendChild(el("dd", {}, [r ? UI.scale({ kind: "rec", pos: r.pos, word: r.word, illustrative: true, label: s }) : value(pageGap("rec_" + s, "no recommendation for this Strategy"))]));
    });
    var sc = $("rail-score");
    sc.appendChild(el("dt", { text: "Credit Score" }));
    sc.appendChild(el("dd", {}, [UI.scale({ kind: "score", pos: I.creditScore.pos, illustrative: true, label: "Credit Score" })]));
    sc.appendChild(el("dt", { text: "Valuation" }));
    sc.appendChild(el("dd", {}, [UI.scale({ kind: "val", pos: I.valuation.pos, illustrative: true, label: "Valuation" })]));
    var dirs = $("rail-dirs");
    dirs.appendChild(el("span", {}, [el("span", { class: "lbl", text: "Direction" }), el("span", { class: dirClass(I.creditDirection.word), text: I.creditDirection.word })]));
    dirs.appendChild(el("span", {}, [el("span", { class: "lbl", text: "Sector" }), el("span", { class: dirClass(I.sectorOutlook.word), text: I.sectorOutlook.word })]));

    var pf = $("rail-pf");
    var g21 = gapDatum("G21");
    pf.appendChild(el("div", { class: "rail__pf" }, [el("button", { type: "button", class: "gap", "data-ref": "G21", "aria-label": "n/a, " + g21.reason }, [el("span", { class: "gap__reason", text: "merger debt not stated" })]), UI.chip("G8")]));
    var note = el("p", { class: "rail__note" }, ["Before merger debt: total ", value(fig("total_leverage_ltm"), "x"), ", net ", value(fig("net_leverage_ltm"), "x"), " (LTM)."]);
    pf.appendChild(note);

    $("rail-risk-illus").appendChild(UI.illus());
    var order = { high: 0, medium: 1, low: 2 };
    var top3 = K.risk.events.slice().sort(function (a, b) {
      var oa = order[String(a.classification).toLowerCase()], ob = order[String(b.classification).toLowerCase()];
      return (oa === undefined ? 3 : oa) - (ob === undefined ? 3 : ob);
    }).slice(0, 3);
    top3.forEach(function (e) {
      $("rail-risks").appendChild(el("li", {}, [el("div", {}, [
        el("a", { href: "#risks" }, [el("b", { text: e.label })]), e.ref ? UI.chip(e.ref) : null,
        el("span", { class: "pi", title: "Probability " + e.probability + ", impact " + e.impact, text: "P " + e.probability + " · I " + e.impact })
      ])]));
    });
    $("rail-foot").textContent = M.runNote + " Run ID: " + (M.runId || "none");
  })();

  /* ---- section index: rail (desktop) and bar (phone), from RBOT_DATA */
  var fitOverall = D.portfolio.fit && D.portfolio.fit.overall ? D.portfolio.fit.overall.v : "N/A";
  var counts = D.counts || {};
  var NAV = [
    { id: "snapshot", label: "Credit Snapshot" },
    { id: "analysis", label: "Analysis", mods: D.modules },
    { id: "model", label: "Model" },
    { id: "portfolio-fit", label: "Portfolio Fit", status: fitOverall },
    { id: "evidence", label: "Evidence", count: String((counts.cited || 0) + (counts.calculated || 0)) },
    { id: "limitations", label: "Limitations", count: String(D.limitations.length) }
  ];
  (function index() {
    var ul = $("rail-index"), mb = $("mbar-list");
    NAV.forEach(function (n) {
      var a = el("a", { href: "#" + n.id, "data-nav-link": n.id }, [el("span", { text: n.label }),
        n.status ? UI.status(n.status) : n.count ? el("span", { class: "index__count", text: n.count }) : null]);
      var li = el("li", {}, [a]);
      if (n.mods) {
        var sub = el("ul", { class: "index__mods", "aria-label": "Modules" });
        n.mods.forEach(function (m) {
          var st = String(m.status).toLowerCase();
          sub.appendChild(el("li", {}, [el("a", { href: "#" + slug(m.id), "data-nav-link": slug(m.id), title: m.name + ": " + m.status }, [
            el("span", { text: m.id }), el("span", { class: "st st--" + st, text: m.status })])]));
        });
        li.appendChild(sub);
      }
      ul.appendChild(li);
      mb.appendChild(el("li", {}, [el("a", { href: "#" + n.id, "data-nav-link": n.id, text: n.label })]));
    });
  })();

  /* ================================================================ header */
  $("title").textContent = "Credit Snapshot: " + M.issuer;
  $("title-meta").appendChild(frag([el("b", { text: M.pathway }), " · " + M.depth + " depth · reporting period " + M.reportingPeriod + " · analysis date " + M.analysisDate + " · analyst ",
    value(M.analyst)]));
  (function provKey() {
    var k = $("prov-key");
    k.appendChild(el("span", {}, [el("i", { class: "prov-swatch prov-swatch--cited" }), "Cited"]));
    k.appendChild(el("span", {}, [el("i", { class: "prov-swatch prov-swatch--calculated" }), "Calculated"]));
    k.appendChild(el("span", {}, [el("span", { class: "prov-model", text: "Model-authored" })]));
    k.appendChild(el("span", {}, [UI.illus()]));
    k.appendChild(el("span", {}, [el("span", { class: "synth", text: "Synthetic" })]));
    k.appendChild(el("span", {}, [el("span", { class: "gap" }, [el("span", { class: "gap__reason", text: "gap, reason on click" })])]));
  })();

  /* ================================================================ front page: the Credit Snapshot */
  var front = $("front");
  var cap = T.capitalStructure, sub = cap.subtotals;
  var recs = {}; I.byInstrument.forEach(function (r) { recs[r.facility] = r; });

  /* 1. key findings (+ thesis line) */
  (function findings() {
    var ol = el("ol", { class: "findings" });
    I.keyFindings.forEach(function (f) { ol.appendChild(el("li", {}, [el("div", {}, [el("span", { class: "prov-model", text: f.text }), chips(f.refs)])])); });
    front.appendChild(card("key-findings", "Key findings", { span: "span-5", meta: [UI.illus()] }, [ol,
      el("p", { class: "card__note" }, ["Thesis, catalysts and the full Snapshot follow below; the thesis is under ", el("a", { href: "#thesis", text: "Investment thesis" }), "."])]));
  })();

  /* 2. capital structure: debt stack chart, the template table in place */
  (function capital() {
    var heads = ["Facility", "~Bloomberg ID (FIGI)", "~Debt type", "~Ratings (M/S)", "Spread / coupon | %", "~CCY", "~Maturity", "Bid", "Ask",
      "Outstanding | US$ m", "Structuring | x", "SSIM | x", "% EV | %", "~Recommendation | illustrative"];
    var t = el("table", { class: "dt dt--framed" }, [el("caption", { class: "vh", text: "Capital structure at " + cap.asOf }), head(heads)]);
    var b = el("tbody"); t.appendChild(b);
    function row(r) {
      var rec = recs[r.facility];
      var cpn = r.coupon && r.coupon.v !== null ? r.coupon : r.coupon;
      b.appendChild(el("tr", {}, [el("th", { scope: "row", text: r.facility }), td(r.figi, { text: true }), el("td", { class: "txt", text: r.debtType }), td(r.ratings, { text: true }),
        td(cpn), el("td", { class: "txt", text: r.ccy }), td(r.maturity, { text: true }), td(r.bid), td(r.ask), td(r.outstanding),
        td(r.structuring_multiple), td(r.ssim_multiple), td(r.pct_ev),
        el("td", { class: "txt" }, [rec ? UI.scale({ kind: "rec", pos: rec.pos, word: rec.word, illustrative: true, label: r.facility }) : ""])]));
    }
    function subtotal(label, d, cls, mult) {
      var r = el("tr", { class: cls || "total" }, [el("th", { scope: "row", colspan: 9, text: label })]);
      r.firstChild.style.textAlign = "right";
      r.appendChild(td(d));
      if (mult) { r.appendChild(td(mult)); r.appendChild(td(mult)); } else r.appendChild(el("td", { colspan: 2 }));
      r.appendChild(el("td", { colspan: 2 }));
      b.appendChild(r);
    }
    var sec = cap.rows.filter(function (r) { return r.rank === "secured"; }), uns = cap.rows.filter(function (r) { return r.rank === "unsecured"; }), oth = cap.rows.filter(function (r) { return r.rank === "other"; });
    sec.forEach(row); subtotal("Senior secured debt", sub.senior_secured, "total", sec[sec.length - 1].structuring_multiple);
    if (uns.length) { uns.forEach(row); subtotal("Unsecured debt", sub.unsecured, "total", uns[uns.length - 1].structuring_multiple); }
    oth.forEach(row);
    subtotal("Total debt", sub.total_debt, "total", cap.rows[cap.rows.length - 1].structuring_multiple);
    subtotal("Cash", sub.cash, "sub");
    subtotal("Net debt", sub.net_debt, "sub");
    subtotal("(Implied) equity at the merger value", sub.implied_equity, "sub");
    subtotal("Equity, listed market value", sub.equity_market_value, "sub");
    subtotal("EV, merger transaction value", sub.ev, "total", sub.ev_multiple);
    subtotal("PF interest", sub.pf_interest, "sub");
    var basis = el("p", { class: "card__note", text: "Multiples on " + cap.ebitda_basis + "." });
    var region = el("div", { class: "expand-region", id: "cap-table", hidden: true, "data-expand": "" }, [
      el("h4", { class: "subhead", text: "Facilities: Structuring and SSIM multiples, % EV, recommendation per instrument" }), scroll(t), basis]);
    var c = card("capital-structure", "Capital structure", { span: "span-7", meta: ["30 June 2026 · x LTM Adj. EBITDA"] }, [debtStack(chartHost()), region]);
    var btn = el("button", { type: "button", class: "bar__btn", "aria-expanded": "false", "aria-controls": "cap-table", text: "Facility table" });
    btn.addEventListener("click", function () { var on = btn.getAttribute("aria-expanded") !== "true"; btn.setAttribute("aria-expanded", String(on)); region.hidden = !on; btn.textContent = on ? "Hide facility table" : "Facility table"; });
    c.querySelector(".bar").appendChild(btn);
    front.appendChild(c);
  })();

  /* 3. the Model chart strip */
  (function strip() {
    var hosts = ["leverage", "coverage", "liquidity"].map(function (k) { return draw("lineStrip", chartHost(), K[k], { height: 132 }); });
    front.appendChild(card("model-strip", "Credit metrics across periods", { meta: ["Model chart strip · FY2023 to LTM Q2 2026"] }, [
      el("div", { class: "chart-strip" }, hosts)
    ]));
  })();

  /* 4. company profile and analyst recommendation */
  (function profile() {
    var p = kvTable("Company profile"), b = p.body;
    kv(b, "Issuer", [value(fig("issuer.name")), tx(" · "), value(fig("issuer.ticker"))]);
    kv(b, "Morningstar Issuer ID", [value(gapDatum("G24"))]);
    kv(b, "Sector / Country", [value(pageGap("sector_country", "sector classification and country of risk are not in the sources", "Company profile"))]);
    kv(b, "Shareholders", [value(pageGap("shareholders", "shareholder register is not in the sources", "Company profile")), tx(" Acquirer under the merger agreement: "), value(fig("issuer.merger.parent"))]);
    kv(b, "Corp ratings (M/S/F)", [value(gapDatum("G25")), tx(" Fitch "), value(gapDatum("G10"))]);
    kv(b, "Issue ratings, secured 2032s (M/S)", [value(fig("trace_czr_12769gac4_moodys")), tx(" / "), value(fig("trace_czr_12769gac4_sp"))]);
    kv(b, "Issue ratings, unsecured 2032s (M/S)", [value(fig("trace_czr_12769gad2_moodys")), tx(" / "), value(fig("trace_czr_12769gad2_sp"))]);
    kv(b, "Outlook (M/S/F)", [value(gapDatum("G11"))]);
    kv(b, "Management", [tx("CEO "), value(fig("issuer.ceo")), tx(" · CFO "), value(fig("issuer.cfo")), tx(" · President and COO "), value(fig("issuer.president_coo"))]);
    kv(b, "Sector Outlook", [el("span", { class: dirClass(I.sectorOutlook.word), text: I.sectorOutlook.word }), UI.illus()]);
    kv(b, "Sponsor Quality", [el("span", { class: "prov-model", text: I.sponsorQuality.word }), UI.illus(), el("div", { class: "card__note" }, [el("span", { class: "prov-model", text: I.sponsorQuality.basis })])]);
    kv(b, "Credit Score", [UI.scale({ kind: "score", pos: I.creditScore.pos, illustrative: true, label: "Credit Score" }), UI.illus()]);
    kv(b, "Credit Direction", [el("span", { class: dirClass(I.creditDirection.word), text: I.creditDirection.word }), UI.illus()]);
    front.appendChild(card("company-profile", "Company profile", { span: "span-6", meta: [M.issuer] }, [p.table]));

    var r = kvTable("Analyst recommendation"), rb = r.body;
    kv(rb, "Analyst", [value(M.analyst)]);
    kv(rb, "Date", [el("span", { class: "num", text: M.analysisDate })]);
    M.strategies.forEach(function (s) {
      var x = I.recommendation[s];
      kv(rb, s, [UI.scale({ kind: "rec", pos: x.pos, word: x.word, illustrative: true, label: s })]);
    });
    kv(rb, "Valuation", [UI.scale({ kind: "val", pos: I.valuation.pos, illustrative: true, label: "Valuation" })]);
    kv(rb, "Credit Score", [UI.scale({ kind: "score", pos: I.creditScore.pos, illustrative: true, label: "Credit Score" })]);
    var guide = el("p", { class: "card__note", text: "Recommendation follows Credit Score (fundamentals) and Valuation (V1 very attractive to V5 very unattractive), per Strategy and per instrument (see the capital structure)." });
    front.appendChild(card("recommendation", "Analyst recommendation", { span: "span-6", meta: [UI.illus()] }, [r.table, guide]));
  })();

  /* 5. transaction summary (Primary flag on) */
  if (M.primary) (function transaction() {
    var lede = el("p", { class: "prose" }, [modelText(I.transactionSummary.text, I.transactionSummary.refs)]);
    var terms = kvTable("Merger terms"), b = terms.body;
    kv(b, "Acquirer", [value(fig("issuer.merger.acquirer_brand")), tx(" via "), value(fig("issuer.merger.parent"))]);
    kv(b, "Agreement date", [value(fig("issuer.merger.agreement_date"))]);
    kv(b, "Price per share (cash)", [value(fig("merger_price_per_share_pr"), "USD")]);
    kv(b, "Transaction value, incl. assumed debt", [value(fig("merger_transaction_value"), "US$ bn")]);
    kv(b, "Assumed Caesars debt", [value(fig("merger_assumed_debt"), "US$ bn")]);
    kv(b, "Premium to unaffected price", [value(fig("merger_premium_unaffected"), "%")]);
    kv(b, "Financing", [value(fig("issuer.merger.financing_condition")), tx("; banks "), value(fig("merger_financing_banks_count"))]);
    kv(b, "End Date", [value(fig("merger_initial_end_date")), tx(", extendable")]);
    kv(b, "Termination fees (company / reverse)", [value(fig("merger_termination_fee"), "USD"), tx(" / "), value(fig("merger_reverse_termination_fee"), "USD")]);
    var g8 = gapDatum("G8"), g28 = gapDatum("G28");
    var crGap = pageGap("cr_score", "no Covenant Review score in the sources", "Transaction summary");
    var tranche = el("tr", {}, [el("th", { scope: "row", text: F["issuer.merger.parent"].v }), td(g28, { text: true }), td(g8, { text: true }), td(g8, { text: true }),
      el("td", { class: "txt" }, [el("span", { class: "prov-model", text: "Acquisition" }), el("span", { class: "tag-model", text: "Model" })]),
      td(g8), td(g8), td(g8), td(g8, { text: true }), td(g8, { text: true }), td(crGap, { text: true }), td(fig("issuer.merger.agreement_date"), { text: true })]);
    var tt = listTable("New debt issues", ["Borrower", "~Bloomberg ID (FIGI)", "~Instrument", "~Debt type", "~UoP", "Tranche size | US$ m", "Guidance / IPT", "OID",
      "~Maturity", "~Exp. ratings", "~CR Score", "~Commit date"], [tranche]);
    front.appendChild(card("transaction", "Transaction summary and new debt issues", { meta: [M.primaryLabel] }, [
      el("div", { class: "cols2" }, [el("div", {}, [lede]), terms.table]),
      el("h4", { class: "subhead", text: "New debt issues" }), tt,
      el("p", { class: "card__note" }, ["The commitment letters name no amount, tranche or pricing, so every tranche field is a gap ", UI.chip("G8"), "."])
    ]));
  })();

  /* 6. business description and EBITDA adjustments (with the EBITDA quality bridge) */
  (function bizAdj() {
    front.appendChild(card("business", "Business description", { span: "span-5", meta: [UI.illus()] }, [
      el("p", { class: "prose" }, [modelText(I.businessDescription.text, I.businessDescription.refs, false)]),
      draw("dumbbell", chartHost(), K.segments)
    ]));
    var adj = T.ebitdaAdjustments, col = 0;
    var steps = adj.rows.map(function (r) {
      var lower = r.label.toLowerCase(), isTotal = r.kind === "total";
      return { label: r.label, short: r.label.replace(" EBITDA", "").replace("Transaction costs and other, net", "Transaction costs").replace("Stock-based compensation", "SBC"),
        kind: isTotal ? "total" : "delta", d: r.cells[col], _l: lower };
    });
    var bridge = { id: "fig-ebitda-quality", title: "EBITDA quality bridge, " + adj.columns[col] + ": Reported to Structuring to SSIM", unit: adj.unit, categoryLabel: "Step",
      summary: "Reported EBITDA of " + adj.rows[0].cells[col].v + " plus marketed add-backs gives Structuring EBITDA of " + steps.filter(function (s) { return /structuring/.test(s._l); })[0].d.v +
        "; no unrealized add-backs are marketed, so SSIM EBITDA is the same.",
      steps: steps, source: "Caesars Q2 2026 earnings release, Adjusted EBITDA reconciliation; owner's definitions (Structuring = Reported + issuer add-backs; SSIM = Structuring − unrealized)" };
    front.appendChild(card("ebitda-adjustments", "EBITDA adjustments", { span: "span-7", meta: ["Reported → Structuring → SSIM · " + adj.unit] }, [
      draw("waterfall", chartHost(), bridge, { height: 210 }),
      periodGrid(adj),
      adj.note ? el("p", { class: "card__note", text: adj.note }) : null
    ]));
  })();

  /* 7. thesis and catalysts */
  front.appendChild(card("thesis", "Investment thesis", { span: "span-6", meta: [UI.illus()] }, [el("p", { class: "prose" }, [modelText(I.thesis.text, I.thesis.refs, false)])]));
  (function catalysts() {
    var ul = el("ul", { class: "catalysts" });
    I.catalysts.forEach(function (c) { ul.appendChild(el("li", {}, [modelText(c.text, c.refs, false)])); });
    front.appendChild(card("catalysts", "Catalysts and near-term events", { span: "span-6", meta: [UI.illus()] }, [ul]));
  })();

  /* 8. credit summary: strengths, weaknesses, historical performance */
  function rowsList(items) {
    var ul = el("ul", { class: "rows" });
    items.forEach(function (s) { ul.appendChild(el("li", {}, [el("b", { text: s.label }), el("span", {}, [modelText(s.text, s.refs, false)])])); });
    return ul;
  }
  front.appendChild(card("strengths", "Strengths", { span: "span-6", meta: [UI.illus()] }, [rowsList(I.strengths)]));
  front.appendChild(card("weaknesses", "Weaknesses", { span: "span-6", meta: [UI.illus()] }, [rowsList(I.weaknesses)]));
  front.appendChild(card("historical", "Historical performance", { meta: [UI.illus()] }, [
    el("div", { class: "mod__grid" }, [
      el("p", { class: "prose" }, [modelText(I.historicalPerformance.text, I.historicalPerformance.refs, false)]),
      draw("columns", chartHost(), K.revenueEbitda, { height: 210 })
    ])
  ]));

  /* 9-11. financials, balance sheet, credit metrics */
  front.appendChild(card("financials", "Financials", { meta: [T.financials.unit + " · LTM in place of PF (no PF LTM: G21)"] }, [periodGrid(T.financials), el("p", { class: "card__note", text: T.financials.note })]));
  front.appendChild(card("balance-sheet", "Balance sheet", { span: "span-6", meta: [T.balanceSheet.unit] }, [periodGrid(T.balanceSheet, { wrap: true })]));
  front.appendChild(card("credit-metrics", "Credit metrics", { span: "span-6", meta: [T.creditMetrics.unit + " · company Adjusted EBITDA"] }, [periodGrid(T.creditMetrics, { wrap: true }),
    T.creditMetrics.note ? el("p", { class: "card__note", text: T.creditMetrics.note }) : null]));

  /* risks: the probability and impact matrix the rail's top three come from */
  front.appendChild(card("risks", "Key risks", { meta: [UI.illus()] }, [draw("riskMatrix", chartHost(), K.risk)]));

  /* 12-13. loan and high-yield relative value */
  var idxGap = pageGap("bloomberg_index_statistics", "Bloomberg index statistics are not in the Source Pack", "Loan and high-yield relative value");
  function indexTable(caption, cols) {
    var trs = ["Ba", "Ba/B", "B", "Caa"].map(function (b) {
      return el("tr", {}, [el("th", { scope: "row", text: b })].concat(cols.slice(1).map(function () { return td(idxGap); })));
    });
    return listTable(caption, cols, trs);
  }
  var histGap = pageGap("price_history", "price history is not in the sources; TRACE pages give the last trade only, and no loan marks are supplied", "Loan and high-yield relative value");
  (function loanRv() {
    var g18 = gapDatum("G18"), g28 = gapDatum("G28"), g25 = gapDatum("G25");
    var hist = histGap;
    var loans = cap.rows.filter(function (r) { return /Term Loan/.test(r.debtType); });
    var trs = loans.map(function (r) {
      return el("tr", {}, [el("th", { scope: "row", text: r.facility }), td(g28, { text: true }), td(g25, { text: true }), td(r.outstanding), td(g18), td(r.maturity, { text: true }),
        el("td", { class: "txt", text: r.debtType }), td(g18), td(hist), td(hist), td(g18), td(g18)]);
    });
    front.appendChild(card("loan-rv", "Loan relative value", { meta: ["Source: Bloomberg US Leveraged Loan Index"] }, [
      el("div", { class: "mod__grid" }, [
        naChart(chartHost(), { id: "fig-loan-curve", title: "Loan spread against maturity", summary: "Would place each CZR term loan's 3-year discount margin against the Ba and B index levels.",
          needs: "Needs loan margins and bids or asks for the CZR term loans, and Bloomberg index levels.", refs: ["G18"] }),
        el("div", {}, [el("h4", { class: "subhead", text: "Index statistics" }), indexTable("Loan index statistics", ["Index", "~Bloomberg ID", "Market value | US$ bn", "Avg price", "Δ 1M", "Δ YTD", "YTM | %", "3Y DM | bp"])])
      ]),
      el("h4", { class: "subhead", text: "Comparables: CZR term loans" }),
      listTable("Loan comparables", ["Facility", "~FIGI", "~Ratings", "Size | US$ m", "Margin | bp", "~Maturity", "~Seniority", "Mid", "Δ 1M", "Δ YTD", "Mid YTM | %", "Mid 3Y DM | bp"], trs)
    ]));
  })();
  (function hyRv() {
    var g19 = gapDatum("G19"), g28 = gapDatum("G28");
    var sizes = {};
    cap.rows.forEach(function (r) { if (r.maturity && r.maturity.v) sizes[r.maturity.v] = r.outstanding; });
    var trs = T.trace.rows.map(function (r) {
      var size = r.issuer === "CZR" && sizes[r.maturity.v] ? sizes[r.maturity.v] : pageGap("peer_issue_size", "issue size of the MGM and PENN notes is not in the sources", "High-yield relative value");
      var senior = r.issuer === "CZR" ? el("td", { class: "txt", text: r.seniority }) : el("td", { class: "txt" }, [el("span", { class: "prov-model", text: r.seniority }), el("span", { class: "tag-model", text: "Model" })]);
      var ratings = el("td", { class: "txt" }, [value(r.moodys), tx(" / "), value(r.sp)]);
      return el("tr", {}, [el("th", { scope: "row", text: r.issuer + " " + r.cusip }), td(g28, { text: true }), ratings, td(size), td(r.coupon), td(r.maturity, { text: true }), senior,
        td(r.price), td(histGap), td(histGap), td(r.yield), td(g19)]);
    });
    front.appendChild(card("hy-rv", "High-yield relative value", { meta: ["Source: Bloomberg US Corporate High Yield Index; FINRA TRACE"] }, [
      el("div", { class: "mod__grid" }, [
        draw("scatter", chartHost(), K.yieldCurve, { height: 250 }),
        el("div", {}, [el("h4", { class: "subhead", text: "Index statistics" }), indexTable("High-yield index statistics", ["Index", "~Bloomberg ID", "Avg coupon | %", "Market value | US$ bn", "Avg price", "Δ 1M", "Δ YTD", "YTW | %", "OAS | bp"])])
      ]),
      el("h4", { class: "subhead", text: "Comparables: TRACE last trades, " + T.trace.title.replace(/^TRACE observations, /, "") }),
      listTable("High-yield comparables", ["Issue (CUSIP)", "~FIGI", "~Ratings (M/S)", "Size | US$ m", "Coupon | %", "~Maturity", "~Seniority", "Last price", "Δ 1M", "Δ YTD", "Last yield | %", "OAS | bp"], trs),
      T.trace.note ? el("p", { class: "card__note", text: T.trace.note }) : null
    ]));
  })();

  /* ================================================================ drill-down: analysis by module */
  function finding(item) { return el("p", {}, [modelText(item.text, item.refs)]); }
  function liqSpec() {
    var rows = T.liquidity.rows, n = rows.length;
    var shortL = ["Cash", "CEI RCF capacity", "CVA RCF capacity", "Letters of credit", "Specific reserves", "Regulatory", "Total liquidity"];
    return { id: "fig-liquidity-build", title: "Liquidity build, " + T.liquidity.title.replace(/^Liquidity at /, ""), unit: T.liquidity.unit, categoryLabel: "Component",
      summary: "Cash of " + rows[0].cell.v + " plus net revolver capacity, less committed reserves, gives " + rows[n - 1].cell.v + " of liquidity.",
      steps: rows.map(function (r, i) { return { label: r.label, short: shortL[i] || r.label, kind: (i === 0 || i === n - 1) ? "total" : "delta", d: r.cell }; }),
      source: "Caesars Q2 2026 earnings release liquidity table" };
  }
  function countSpec(id, title, summary, cats, vals, unit) {
    return { id: id, title: title, unit: unit || "count", categories: cats, categoryLabel: "Group", summary: summary,
      series: [{ key: "n", label: "Records", values: vals.map(function (v) { return { v: String(v), prov: "calculated" }; }) }], source: "Counted on this page from the run's evidence register" };
  }
  var FILE_SHORT = [[/10Q/i, "CZR 10-Q"], [/10K/i, "CZR 10-K"], [/^CZR_Q2.*Earnings/i, "CZR release"], [/Merger_Agreement/i, "Merger 8-K"], [/Merger_Press/i, "Merger release"],
    [/^MGM_Q2/i, "MGM release"], [/^PENN_Q2/i, "PENN release"], [/TRACE_12769GAC4/i, "TRACE CZR SS"], [/TRACE_12769GAD2/i, "TRACE CZR SU"], [/TRACE_552953/i, "TRACE MGM"],
    [/TRACE_707569/i, "TRACE PENN"], [/Constraints_Compliance/i, "CLO limits"], [/Exposure_Report/i, "CLO exposure"], [/Mandate/i, "CLO mandate"]];
  function fileShort(f) { for (var i = 0; i < FILE_SHORT.length; i++) if (FILE_SHORT[i][0].test(f)) return FILE_SHORT[i][1]; return f; }
  var byFile = {};
  Object.keys(D.citations).forEach(function (k) { var c = D.citations[k]; (byFile[c.file] = byFile[c.file] || []).push(c); });
  var files = Object.keys(byFile);

  /* Per-module content: headline finding(s), headline chart, detail. Status, name and reason always come from D.modules. */
  var MODS = {
    "CP-0": {
      lede: function () { return []; },
      chart: function () {
        var cats = files.map(fileShort), vals = files.map(function (f) { return byFile[f].length; });
        return draw("columns", chartHost(), countSpec("fig-files", "Citations by source file", files.length + " files in the Source Pack carry the run's " + Object.keys(D.citations).length + " cited and synthetic records.", cats, vals), { height: 220 });
      },
      detail: function () {
        var trs = files.map(function (f) { return el("tr", {}, [el("th", { scope: "row", text: f }), el("td", { class: "num", text: String(byFile[f].length) }), el("td", { class: "txt", text: byFile[f][0].synthetic ? "Synthetic portfolio file" : "Issuer, market or peer document" })]); });
        return [listTable("Source Pack files", ["File", "Citations", "~Kind"], trs)];
      }
    },
    "CP-1": {
      lede: function () { return [finding(I.keyFindings[0]), finding(I.keyFindings[2])]; },
      chart: function () { return draw("stackedColumns", chartHost(), K.maturityWall, { height: 230 }); },
      detail: function () {
        var trs = T.maturities.rows.map(function (r) { return el("tr", {}, [el("th", { scope: "row", text: r.label }), td(r.cell)]); });
        var face = cap.rows.map(function (r) { return el("tr", {}, [el("th", { scope: "row", text: r.facility }), td(r.outstanding), td(r.book), td(r.maturity, { text: true })]); });
        return [el("div", { class: "cols2" }, [
          el("div", {}, [el("h4", { class: "subhead", text: T.maturities.title }), listTable(T.maturities.title, ["Year", "Amount | " + T.maturities.unit], trs)]),
          el("div", {}, [el("h4", { class: "subhead", text: "Face and book value at " + cap.asOf }), listTable("Face and book", ["Facility", "Face | US$ m", "Book | US$ m", "~Maturity"], face)])
        ]), el("p", { class: "card__note", text: K.maturityWall.note || "" })];
      }
    },
    "CP-1B": {
      lede: function () { return [finding(I.weaknesses[2]), finding(I.strengths[2])]; },
      chart: function () { return draw("waterfall", chartHost(), K.ebitdaBridge, { height: 240 }); },
      detail: function () { return [el("h4", { class: "subhead", text: T.segments.title }), periodGrid(T.segments)]; }
    },
    "CP-2": {
      lede: function () { return [finding(I.keyFindings[1]), finding(I.strengths[1])]; },
      chart: function () { return draw("waterfall", chartHost(), liqSpec(), { height: 240 }); },
      detail: function () {
        return [el("div", { class: "cols2" }, [
          naChart(chartHost(), { id: "fig-liquidity-bridge", title: "Liquidity bridge, 12 months", summary: "Would bridge accessible liquidity from 30 June 2025 to 30 June 2026 through cash interest, taxes, capex and debt service.",
            needs: "Needs liquidity at the start of the period and quarterly cash flows, which the Source Pack does not state.", refs: ["G16", "G3"] }),
          el("div", {}, [el("h4", { class: "subhead", text: T.liquidity.title }), listTable(T.liquidity.title, ["Component", "Amount | " + T.liquidity.unit],
            T.liquidity.rows.map(function (r, i, a) { return el("tr", { class: i === a.length - 1 ? "total" : null }, [el("th", { scope: "row", text: r.label }), td(r.cell)]); }))])
        ])];
      }
    },
    "CP-3": {
      lede: function () { return [finding(I.keyFindings[3]), el("p", {}, ["Valuation ", UI.scale({ kind: "val", pos: I.valuation.pos, illustrative: true, label: "Valuation" }), UI.illus()])]; },
      chart: function () { return draw("rangeStrip", chartHost(), K.peerRange); },
      detail: function () {
        var trs = I.byInstrument.map(function (r) { return el("tr", {}, [el("th", { scope: "row", text: r.facility }), el("td", { class: "txt" }, [UI.scale({ kind: "rec", pos: r.pos, word: r.word, illustrative: true, label: r.facility })])]); });
        return [el("h4", { class: "subhead", text: "Recommendation per instrument" }), listTable("Recommendation per instrument", ["Instrument", "~Recommendation | illustrative"], trs),
          el("p", { class: "card__note" }, [K.peerRange.note || ""])];
      }
    },
    "CP-4": {
      lede: function () { return [el("p", {}, ["Financing: ", value(fig("issuer.merger.financing_condition")), ". Termination fees ", value(fig("merger_termination_fee"), "USD"), " (company) and ", value(fig("merger_reverse_termination_fee"), "USD"), " (reverse)."])]; },
      chart: function () { return draw("bullet", chartHost(), K.covenant); },
      detail: function () {
        return [el("p", { class: "prose" }, ["Covenant headroom needs the CEI credit agreement and its amendments; they are not in the extraction ", UI.chip("G17"),
          ". The current basis is net leverage ", value(fig("net_leverage_ltm"), "x"), ", printed without a test level."])];
      }
    },
    "CP-5": {
      lede: function () { return []; },
      chart: function () {
        var c = D.counts || {};
        return draw("columns", chartHost(), countSpec("fig-records", "Records behind this Report, by origin", "Cited " + c.cited + ", calculated " + c.calculated + ", gaps " + c.gaps + ", synthetic " + c.synthetic_sources + ".",
          ["Cited", "Calculated", "Gaps", "Synthetic"], [c.cited, c.calculated, c.gaps, c.synthetic_sources]), { height: 200 });
      },
      detail: function () {
        return [el("p", { class: "prose" }, ["Every figure on the page opens its citation (file, line, excerpt) or its formula. The register is under ",
          el("a", { href: "#evidence", text: "Evidence" }), "; gaps are under ", el("a", { href: "#limitations", text: "Limitations" }), "."])];
      }
    },
    "CP-6": {
      lede: function () { return [el("p", {}, [UI.status(D.portfolio.fit.overall.v), " ", el("span", { class: "prov-model", text: D.portfolio.fit.summary }), UI.illus(), el("span", { class: "synth", text: "Synthetic" })])]; },
      chart: function () { return draw("bullet", chartHost(), K.cloLimits); },
      detail: function () { return [el("p", { class: "prose" }, ["The full check, per instrument, is under ", el("a", { href: "#portfolio-fit", text: "Portfolio Fit" }), "."])]; }
    }
  };

  (function modules() {
    var host = $("modules");
    var n = { }; D.modules.forEach(function (m) { n[m.status] = (n[m.status] || 0) + 1; });
    var meta = $("analysis-meta");
    meta.appendChild(tx(D.modules.length + " modules · " + Object.keys(n).map(function (k) { return n[k] + " " + k; }).join(" · ")));
    var toggleAll = el("button", { type: "button", class: "btn", "aria-pressed": "false", text: "Expand all" });
    meta.appendChild(toggleAll);
    toggleAll.addEventListener("click", function () {
      var on = toggleAll.getAttribute("aria-pressed") !== "true";
      toggleAll.setAttribute("aria-pressed", String(on)); toggleAll.textContent = on ? "Collapse all" : "Expand all";
      host.querySelectorAll("details.mod__more").forEach(function (d) { d.open = on; });
    });
    $("analysis-lede").appendChild(tx("Each module opens on its headline finding and chart; Show detail opens its analysis. Statuses are the run's own: Restricted means the module answers its question with the gaps named beside it."));
    D.modules.forEach(function (m) {
      var spec = MODS[m.id] || { lede: function () { return []; }, chart: function () { return null; }, detail: function () { return []; } };
      var why = el("p", { class: "mod__why" }, [el("b", { text: m.status + ". " }), m.reason + " ", chips(m.refs)]);
      var lede = el("div", { class: "mod__lede" }, spec.lede().concat([why]));
      var chart = spec.chart();
      var detail = el("details", { class: "xp xp--light mod__more" }, [el("summary", { text: "Analysis and tables" }), el("div", { class: "xp__body stack" }, spec.detail())]);
      var id = slug(m.id);
      var bar = el("h3", { class: "bar", id: id + "-h" }, [el("span", { text: m.id + " · " + m.name }), el("span", { class: "on-navy" }, [UI.status(m.status)])]);
      host.appendChild(el("section", { class: "block card", id: id, "data-nav": id, "aria-labelledby": id + "-h" }, [bar,
        el("div", { class: "card__body" }, [chart ? el("div", { class: "mod__grid" }, [lede, chart]) : lede, detail])]));
    });
  })();

  /* ================================================================ Model: collapsible bands */
  (function model() {
    var fin = T.financials;
    var pl = function (r) { return /^(Revenue|% Δ|Gross Profit|EBITDA|% margin)/.test(r.label); };
    $("model-meta").appendChild(tx("US$ m · click any cell for its passport (source, locator, excerpt or formula)"));
    var body = $("model-body");
    body.appendChild(el("p", { class: "part__lede" }, ["LTM Adjusted EBITDA ", value(fig("ltm_adj_ebitda_q2_2026")), " against total debt ", value(fig("total_debt_face_2026_06_30")),
      "; cash interest on debt is estimated to fall in 2026 and 2027."]));
    body.appendChild(el("div", { class: "mod__grid" }, [draw("lineStrip", chartHost(), K.interestPath, { height: 200 }), el("div", { class: "stack" }, [periodGrid(T.creditMetrics, { wrap: true }),
      el("p", { class: "card__note", text: "Bands below follow the model: earnings, the adjusted EBITDA bridge, the cash flow waterfall, the debt stack by rank and the credit metrics. Each opens to its period grid." })])]));
    var rankRows = [];
    ["secured", "unsecured", "other"].forEach(function (rk) {
      var rs = cap.rows.filter(function (r) { return r.rank === rk; });
      rs.forEach(function (r) { rankRows.push(el("tr", { class: "indent" }, [el("th", { scope: "row", text: r.facility }), el("td", { class: "txt", text: r.debtType }), td(r.outstanding), td(r.book), td(r.structuring_multiple), td(r.pct_ev)])); });
      var st = rk === "secured" ? sub.senior_secured : rk === "unsecured" ? sub.unsecured : sub.other;
      rankRows.push(el("tr", { class: "total" }, [el("th", { scope: "row", text: { secured: "Senior secured", unsecured: "Unsecured", other: "Other" }[rk] }), el("td"), td(st), el("td"), td(rs[rs.length - 1].structuring_multiple), td(rs[rs.length - 1].pct_ev)]));
    });
    rankRows.push(el("tr", { class: "total" }, [el("th", { scope: "row", text: "Total debt (check)" }), el("td"), td(sub.total_debt_check), el("td"), el("td"), el("td")]));
    var bands = el("div", { class: "bands" }, [
      more("Earnings", [periodGrid(fin, { filter: pl }), el("h4", { class: "subhead", text: T.segments.title }), periodGrid(T.segments)]),
      more("Adjusted EBITDA bridge", [el("div", { class: "mod__grid" }, [periodGrid(T.ebitdaAdjustments), draw("waterfall", chartHost(), K.ebitdaBridge, { id: "fig-ebitda-bridge-model", height: 230 })])]),
      more("Cash flow waterfall", [el("div", { class: "mod__grid" }, [periodGrid(fin, { filter: function (r) { return !pl(r); } }), draw("waterfall", chartHost(), K.cashBridge, { height: 230 })])]),
      more("Debt stack by rank", [listTable("Debt stack by rank", ["Facility", "~Debt type", "Face | US$ m", "Book | US$ m", "Cumulative | x", "% EV | %"], rankRows)]),
      more("Credit metrics", [periodGrid(T.creditMetrics, { wrap: true }), periodGrid(T.balanceSheet, { wrap: true })])
    ]);
    body.appendChild(bands);
  })();

  /* ================================================================ Portfolio Fit (Test CLO I, synthetic) */
  (function portfolio() {
    var P = D.portfolio, fitD = P.fit;
    var meta = $("pf-meta");
    meta.appendChild(el("span", { class: "on-navy" }, [UI.status(fitD.overall.v), UI.illus(), el("span", { class: "synth", text: "Synthetic" })]));
    meta.appendChild(tx(P.name + " · as of " + P.asOf));
    var b = $("pf-body");
    var checks = fitD.checks.map(function (c) {
      return el("tr", {}, [el("th", { scope: "row", text: c.constraint }), el("td", { class: "num", text: c.limit }), td({ v: c.current, prov: "synthetic", ref: c.ref }), td({ v: c.headroom, prov: "synthetic", ref: c.ref }),
        el("td", { class: "txt" }, [UI.status(c.result)]), el("td", { class: "excerpt", text: c.note || "" })]);
    });
    var inst = fitD.byInstrument.map(function (r) { return el("tr", {}, [el("th", { scope: "row", text: r.instrument }), el("td", { class: "txt" }, [UI.status(r.fit)]), el("td", { class: "excerpt", text: r.note || "" })]); });
    var sumT = kvTable("Portfolio summary");
    Object.keys(P.summary).forEach(function (k) { kv(sumT.body, k, [value(P.summary[k])]); });
    var mand = kvTable("Mandate");
    Object.keys(P.mandate).forEach(function (k) { kv(mand.body, k, [value(P.mandate[k])]); });
    var cons = P.constraints.map(function (c) {
      return el("tr", {}, [el("th", { scope: "row", text: c.id }), el("td", { class: "txt", text: c.category }), el("td", { class: "txt", text: c.parameter }), el("td", { class: "num", text: c.limit }),
        el("td", { class: "txt", text: c.breachType }), td({ v: c.current, prov: "synthetic", ref: c.ref }), td({ v: c.headroom, prov: "synthetic", ref: c.ref }), el("td", { class: "txt" }, [UI.status(c.status)])]);
    });
    b.appendChild(el("section", { class: "block card", id: "pf-summary", "aria-labelledby": "pf-summary-h" }, [
      el("h3", { class: "bar", id: "pf-summary-h" }, [el("span", { text: "Fit for " + P.name }), el("span", { class: "bar__meta", text: "Synthetic portfolio; the fit call is illustrative" })]),
      el("div", { class: "card__body" }, [
        el("div", { class: "mod__grid" }, [
          el("p", { class: "prose" }, [UI.status(fitD.overall.v), " ", el("span", { class: "prov-model", text: fitD.summary }), UI.illus()]),
          draw("rangeStrip", chartHost(), K.cloSectors)
        ]),
        listTable("Checks", ["Constraint", "Limit", "Current", "Headroom", "~Result", "~Note"], checks),
        more("Per instrument, portfolio summary, all constraints and the mandate", [
          el("h4", { class: "subhead", text: "Fit per instrument" }), listTable("Fit per instrument", ["Instrument", "~Fit", "~Note"], inst),
          el("div", { class: "cols2" }, [el("div", {}, [el("h4", { class: "subhead", text: "Portfolio summary" }), sumT.table]), el("div", {}, [el("h4", { class: "subhead", text: "Mandate" }), mand.table])]),
          el("h4", { class: "subhead", text: "Constraints compliance monitor" }),
          listTable("Constraints", ["ID", "~Category", "~Parameter", "Limit", "~Breach type", "Current", "Headroom", "~Status"], cons)
        ])
      ])
    ]));
  })();

  /* ================================================================ Evidence */
  (function evidence() {
    var c = D.counts || {};
    $("ev-meta").appendChild(tx(c.cited + " cited · " + c.calculated + " calculated · " + c.synthetic_sources + " synthetic"));
    var b = $("ev-body");
    b.appendChild(el("p", { class: "part__lede", text: "Every citation with its verbatim excerpt, every calculation with its formula. Select an ID to open it beside the analysis, with every place it is used." }));
    var input = el("input", { type: "search", id: "ev-q", placeholder: "Figure, value, file or ID", autocomplete: "off" });
    var out = el("output", { for: "ev-q", "aria-live": "polite" });
    b.appendChild(el("div", { class: "search" }, [el("label", { for: "ev-q", text: "Find in the evidence" }), input, out]));
    var bands = el("div", { class: "bands", id: "ev-bands" });
    function idBtn(ref) {
      var cls = ref.charAt(0) === "K" ? "calc" : "cite";
      return el("button", { type: "button", class: cls, "data-drawer-ref": ref, "aria-label": "Open " + ref + " beside the analysis", text: ref });
    }
    files.forEach(function (f) {
      var rows = byFile[f].map(function (ci) {
        return el("tr", { "data-ev": "" }, [el("td", { class: "ev-id" }, [idBtn(ci.id)]), el("td", { class: "txt", text: ci.label || ci.key || "" }), el("td", { class: "num", text: ci.value == null ? "" : String(ci.value) }),
          el("td", { class: "txt", text: ci.period || "" }), el("td", { class: "txt", text: ci.locator || "" }), el("td", { class: "excerpt", text: ci.excerpt || "" })]);
      });
      var d = more(f + " (" + rows.length + ")", [listTable(f, ["~ID", "~Figure", "Value", "~Period", "~Locator", "~Excerpt"], rows)]);
      if (byFile[f][0].synthetic) d.querySelector("summary").appendChild(el("span", { class: "synth", text: "Synthetic" }));
      bands.appendChild(d);
    });
    var krows = Object.keys(D.calcs).map(function (k) {
      var ca = D.calcs[k];
      return el("tr", { "data-ev": "" }, [el("td", { class: "ev-id" }, [idBtn(ca.id)]), el("td", { class: "txt", text: ca.label || "" }), el("td", { class: "num", text: ca.value == null ? "" : String(ca.value) }),
        el("td", { class: "txt", text: ca.period || "" }), el("td", { class: "excerpt" }, [el("code", { text: ca.formula || "" })]), el("td", { class: "txt" }, [chips(ca.inputs)])]);
    });
    bands.appendChild(more("Calculations (" + krows.length + ")", [listTable("Calculations", ["~ID", "~Figure", "Value", "~Period", "~Formula", "~Inputs"], krows)]));
    b.appendChild(bands);
    input.addEventListener("input", function () {
      var q = input.value.trim().toLowerCase(), hits = 0;
      bands.querySelectorAll("details").forEach(function (d) {
        var any = 0;
        d.querySelectorAll("tr[data-ev]").forEach(function (tr) { var ok = !q || tr.textContent.toLowerCase().indexOf(q) >= 0; tr.hidden = !ok; if (ok) any++; });
        d.hidden = q && !any; d.open = !!(q && any); hits += any;
      });
      out.textContent = q ? hits + " match" + (hits === 1 ? "" : "es") : "";
    });
  })();

  /* ================================================================ Limitations */
  function limitations() {
    var L = D.limitations, byScope = {};
    L.forEach(function (l) { (byScope[l.scope] = byScope[l.scope] || []).push(l); });
    var scopes = Object.keys(byScope);
    $("lim-meta").appendChild(tx(L.length + " stated at Approval · " + PAGE_GAPS.length + " found on this page"));
    var b = $("lim-body");
    b.appendChild(el("p", { class: "part__lede", text: L.length + " limitations were stated at Approval (" + scopes.map(function (s) { return byScope[s].length + " " + s; }).join("; ") +
      "). The page then drew " + PAGE_GAPS.length + " more n/a cells for fields no gap record covers; they are listed below as unforeseen." }));
    var known = L.map(function (l) {
      return el("tr", {}, [el("td", { class: "ev-id" }, [UI.chip(l.ref)]), el("td", { class: "txt", text: l.field }), el("td", { class: "excerpt", text: l.text }), el("td", { class: "txt", text: l.scope }), el("td", { class: "txt", text: l.origin })]);
    });
    var un = PAGE_GAPS.map(function (g) { return el("tr", {}, [el("td", { class: "txt", text: g.field }), el("td", { class: "excerpt", text: g.reason }), el("td", { class: "txt", text: g.where })]); });
    b.appendChild(el("section", { class: "block card", id: "lim-known", "aria-labelledby": "lim-known-h" }, [
      el("h3", { class: "bar", id: "lim-known-h" }, [el("span", { text: "Known at Approval" }), el("span", { class: "bar__meta", text: L.length + " records" })]),
      el("div", { class: "card__body" }, [
        el("div", { class: "mod__grid" }, [el("p", { class: "prose", text: "The PF-LTM column is the model limitation that matters most: without the merger's new debt, no pro forma leverage or interest cover can be computed." }),
          draw("columns", chartHost(), countSpec("fig-lim-scope", "Limitations by scope", scopes.map(function (s) { return s + ": " + byScope[s].length; }).join("; ") + ".", scopes, scopes.map(function (s) { return byScope[s].length; })), { height: 190 })]),
        more("All " + L.length + " limitations", [listTable("Limitations known at Approval", ["~Gap", "~Field", "~What is missing", "~Scope", "~Logged by"], known)])
      ])
    ]));
    b.appendChild(el("section", { class: "block card", id: "lim-unforeseen", "aria-labelledby": "lim-un-h", style: "margin-top:var(--s-4)" }, [
      el("h3", { class: "bar", id: "lim-un-h" }, [el("span", { text: "Unforeseen" }), el("span", { class: "bar__meta", text: PAGE_GAPS.length + " fields without a gap record" })]),
      el("div", { class: "card__body" }, [PAGE_GAPS.length ? listTable("Unforeseen limitations", ["~Field", "~What is missing", "~Where on the page"], un) : el("p", { class: "prose", text: "None arose during the run." })])
    ]));
  }
  limitations();

  /* ================================================================ charts, then wire the kit */
  DRAWN.forEach(function (f) { f(); });
  UI.init(document);

  /* ================================================================ evidence drawer */
  var shell = $("shell"), drawer = $("drawer"), dBody = $("drawer-body"), dBack = $("drawer-back"), hist = [];
  function lookup(ref) {
    if (D.citations[ref]) return { kind: D.citations[ref].synthetic ? "Synthetic portfolio file" : "Cited", item: D.citations[ref] };
    if (D.calcs[ref]) return { kind: "Calculated", item: D.calcs[ref] };
    if (D.gaps[ref]) return { kind: "Not in the sources", item: D.gaps[ref] };
    return null;
  }
  function drawerChip(ref) {
    var cls = ref.charAt(0) === "K" ? "calc" : ref.charAt(0) === "G" ? "gapref" : "cite";
    return el("button", { type: "button", class: cls, "data-drawer-ref": ref, text: ref });
  }
  function sectionOf(node) {
    var s = node.closest("section[id], details");
    while (s && s.tagName === "DETAILS") s = s.parentElement.closest("section[id], details");
    var card2 = node.closest(".card[id]");
    var target = card2 || s;
    if (!target) return null;
    var hd = target.querySelector("h3, h2");
    var nm = hd ? (hd.firstElementChild && hd.firstElementChild.tagName === "SPAN" ? hd.firstElementChild.textContent : hd.textContent) : target.id;
    return { id: target.id, name: nm.trim() };
  }
  function uses(ref) {
    var seen = {}, out = [];
    document.querySelectorAll('#main [data-ref="' + ref + '"]').forEach(function (n) {
      var s = sectionOf(n); if (!s || seen[s.id]) return; seen[s.id] = true; out.push({ sec: s, node: n });
    });
    return out;
  }
  function goTo(node) {
    var d = node.parentElement;
    while (d) { if (d.tagName === "DETAILS") d.open = true; d = d.parentElement; }
    node.scrollIntoView({ block: "center", behavior: "instant" });
    var tgt = node.closest("td") || node;
    tgt.classList.remove("is-flash"); void tgt.offsetWidth; tgt.classList.add("is-flash");
    if (node.focus) node.focus({ preventScroll: true });
  }
  function renderDrawer(ref) {
    while (dBody.firstChild) dBody.removeChild(dBody.firstChild);
    var f = lookup(ref);
    dBody.appendChild(el("div", { class: "drawer__id" }, [el("b", { text: ref }), el("span", { class: "drawer__kind", text: f ? f.kind : "Unknown reference" }), f && f.item.synthetic ? el("span", { class: "synth", text: "Synthetic" }) : null]));
    if (!f) { dBody.appendChild(el("p", { text: "No record for " + ref + " in this run." })); return; }
    var it = f.item;
    if (f.kind === "Calculated") {
      dBody.appendChild(el("dl", {}, [el("dt", { text: "Figure" }), el("dd", { text: it.label || "" }), el("dt", { text: "Value" }), el("dd", { class: "num", text: (it.value || "") + (it.unit && it.unit !== "text" ? " " + it.unit : "") }),
        el("dt", { text: "Period" }), el("dd", { text: it.period || "" }), el("dt", { text: "Formula" }), el("dd", {}, [el("code", { text: it.formula || "" })])]));
      var ins = el("ul");
      (it.inputs || []).forEach(function (r) { var x = lookup(r); ins.appendChild(el("li", {}, [drawerChip(r), el("span", { text: x ? (x.item.label || x.item.field || "") + (x.item.value ? ": " + x.item.value : "") : "" })])); });
      dBody.appendChild(el("div", {}, [el("h3", { text: "Inputs" }), ins]));
      if (it.note) dBody.appendChild(el("p", { class: "muted", text: it.note }));
    } else if (f.kind === "Not in the sources") {
      var lim = D.limitations.filter(function (l) { return l.ref === ref; })[0];
      dBody.appendChild(el("dl", {}, [el("dt", { text: "Field" }), el("dd", { text: it.field || "" }), el("dt", { text: "Reason" }), el("dd", { text: it.reason || "" }),
        el("dt", { text: "Scope" }), el("dd", { text: lim ? lim.scope : "" }), el("dt", { text: "Logged by" }), el("dd", { text: it.origin || "" })]));
    } else {
      dBody.appendChild(el("dl", {}, [el("dt", { text: "Figure" }), el("dd", { text: it.label || it.key || "" }), el("dt", { text: "Value" }), el("dd", { class: "num", text: it.value == null ? "" : String(it.value) + (it.unit && it.unit !== "text" ? " " + it.unit : "") }),
        el("dt", { text: "Period" }), el("dd", { text: it.period || "" }), el("dt", { text: "File" }), el("dd", { text: it.file || "" }), el("dt", { text: "Locator" }), el("dd", { text: it.locator || "" })]));
      if (it.excerpt) dBody.appendChild(el("blockquote", { text: it.excerpt }));
    }
    var usedBy = Object.keys(D.calcs).filter(function (k) { return (D.calcs[k].inputs || []).indexOf(ref) >= 0; });
    if (usedBy.length) {
      var ub = el("ul");
      usedBy.forEach(function (k) { ub.appendChild(el("li", {}, [drawerChip(k), el("span", { text: D.calcs[k].label + ": " + D.calcs[k].value })])); });
      dBody.appendChild(el("div", {}, [el("h3", { text: "Feeds these calculations" }), ub]));
    }
    var u = uses(ref), ul = el("ul");
    u.forEach(function (x) {
      var btn = el("button", { type: "button", class: "btn btn--quiet", text: "Go to" });
      btn.addEventListener("click", function () { goTo(x.node); });
      ul.appendChild(el("li", {}, [btn, el("span", { text: x.sec.name })]));
    });
    dBody.appendChild(el("div", {}, [el("h3", { text: "Where it appears" }), u.length ? ul : el("p", { class: "muted", text: "Only in the evidence register." })]));
  }
  var lastFocus = null;
  function openDrawer(ref, push) {
    if (push !== false && drawer.dataset.ref && drawer.dataset.ref !== ref && !drawer.hidden) hist.push(drawer.dataset.ref);
    if (drawer.hidden) { lastFocus = document.activeElement; hist = []; }
    drawer.dataset.ref = ref;
    renderDrawer(ref);
    drawer.hidden = false; shell.classList.add("is-drawer");
    dBack.disabled = !hist.length;
    $("drawer-h").focus({ preventScroll: true });
  }
  function closeDrawer() {
    drawer.hidden = true; shell.classList.remove("is-drawer"); delete drawer.dataset.ref; hist = [];
    if (lastFocus && lastFocus.focus && document.contains(lastFocus)) lastFocus.focus();
  }
  $("drawer-close").addEventListener("click", closeDrawer);
  dBack.addEventListener("click", function () { if (hist.length) openDrawer(hist.pop(), false); dBack.disabled = !hist.length; });
  document.addEventListener("click", function (e) {
    var t = e.target.closest ? e.target.closest("[data-drawer-ref]") : null;
    if (t) { e.preventDefault(); UI.close(); openDrawer(t.getAttribute("data-drawer-ref")); }
  });
  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape" && !drawer.hidden && drawer.contains(document.activeElement)) closeDrawer();
  });
  /* The shared popover is the quick look; add one action to it that opens the same record beside the analysis. */
  function decoratePop(pop) {
    if (pop.hidden || pop.querySelector(".pop__more")) return;
    var id = pop.querySelector(".pop__id");
    if (!id) return;
    var ref = id.textContent.trim();
    var b = el("button", { type: "button", class: "btn btn--quiet pop__more", "data-drawer-ref": ref, text: "Open beside the analysis" });
    pop.appendChild(b);
  }
  new MutationObserver(function () {
    var pop = document.querySelector("body > .pop");
    if (pop && !pop.dataset.watched) {
      pop.dataset.watched = "1";
      new MutationObserver(function () { decoratePop(pop); }).observe(pop, { attributes: true, attributeFilter: ["hidden"], childList: true });
      decoratePop(pop);
    }
  }).observe(document.body, { childList: true });

  /* ================================================================ navigation: where am I, deep links */
  var links = document.querySelectorAll("[data-nav-link]");
  function setCurrent(id) {
    var parent = null;
    D.modules.forEach(function (m) { if (slug(m.id) === id) parent = "analysis"; });
    links.forEach(function (a) {
      var k = a.getAttribute("data-nav-link");
      if (k === id || k === parent) a.setAttribute("aria-current", "location"); else a.removeAttribute("aria-current");
    });
    var mb = document.querySelector('#mbar-list [aria-current="location"]');
    if (mb && mb.scrollIntoView && window.matchMedia("(max-width: 900px)").matches) {
      var ul = $("mbar-list"); ul.scrollLeft = mb.offsetLeft - 16;
    }
  }
  var targets = Array.prototype.slice.call(document.querySelectorAll("[data-nav]"));
  var io = null;
  if ("IntersectionObserver" in window) {
    var visible = {};
    io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) { visible[en.target.getAttribute("data-nav")] = en.isIntersecting; });
      var cur = null;
      targets.forEach(function (t) { if (visible[t.getAttribute("data-nav")]) cur = t.getAttribute("data-nav"); });
      if (cur) setCurrent(cur);
    }, { rootMargin: "-20% 0px -70% 0px" });
    targets.forEach(function (t) { io.observe(t); });
  }
  setCurrent("snapshot");
  function openTarget(hash, focus) {
    if (!hash || hash.length < 2) return;
    var t = document.getElementById(decodeURIComponent(hash.slice(1)));
    if (!t) return;
    var d = t.parentElement;
    while (d) { if (d.tagName === "DETAILS") d.open = true; d = d.parentElement; }
    var own = t.querySelector(":scope > .card__body > details.mod__more");
    if (own) own.open = true;
    if (focus) {
      var hd = t.querySelector("h2, h3");
      if (hd) { if (!hd.hasAttribute("tabindex")) hd.setAttribute("tabindex", "-1"); hd.focus({ preventScroll: true }); }
    }
  }
  window.addEventListener("hashchange", function () { openTarget(location.hash, true); });
  if (location.hash) { openTarget(location.hash, false); var t0 = document.getElementById(location.hash.slice(1)); if (t0) t0.scrollIntoView({ behavior: "instant" }); }

  /* ================================================================ print: expand everything, restore after */
  var printOpened = [];
  window.addEventListener("beforeprint", function () {
    printOpened = [];
    document.querySelectorAll("details:not([open])").forEach(function (d) { d.open = true; printOpened.push(d); });
  });
  window.addEventListener("afterprint", function () { printOpened.forEach(function (d) { d.open = false; }); printOpened = []; });

  /* ================================================================ review states (?demo=expanded, ?demo=drawer) */
  var demo = (location.search.match(/[?&]demo=([a-z]+)/) || [])[1];
  if (demo === "expanded") {
    ["cp-4", "cp-5"].forEach(function (id) { var d = document.querySelector("#" + id + " details.mod__more"); if (d) d.open = true; });
    var anchor = document.getElementById("cp-4");
    var cell = document.querySelector("#cp-4 .cite");
    var openPop = function () {
      anchor.scrollIntoView({ block: "start", behavior: "instant" });
      if (cell) UI.open(cell.getAttribute("data-ref"), cell);
      setCurrent("cp-4");
    };
    if (document.fonts && document.fonts.ready) document.fonts.ready.then(function () { requestAnimationFrame(openPop); }); else openPop();
  } else if (demo === "drawer") {
    var cap2 = document.querySelector("#key-findings .calc");
    if (cap2) openDrawer(cap2.getAttribute("data-ref"));
  } else if (demo === "print") {
    document.querySelectorAll("details:not([open])").forEach(function (d) { d.open = true; });
  }
  document.documentElement.setAttribute("data-ready", "1");
})();
