/* RBOT Report mockup A: IC paper as an app shell.
   A persistent left navigation pane and a set of hash-routed views: the Credit Snapshot (a summary
   screen), one view per module with its full analysis, then Model, Portfolio Fit, Evidence and
   Limitations. Built from window.RBOT_DATA with the shared RBOTUI / RBOTCharts layer. Every figure is
   a Datum printed as served; every judgement carries the ILLUSTRATIVE tag; module statuses, names and
   limitations are read at runtime. No innerHTML anywhere. */
(function () {
  "use strict";
  var D = window.RBOT_DATA, UI = window.RBOTUI, C = window.RBOTCharts, el = UI.el;
  var I = D.illustrative, F = D.figures, T = D.tables, K = D.charts, P = D.portfolio, M = D.meta, OM = T.operatingModel;
  var charts = [], figs = {}, figN = 0, curView = "snapshot";
  var main = document.getElementById("main");
  var VIEWS = {}, ORDER = [];

  /* ------------------------------------------------------------ small helpers */
  function txt(s) { return document.createTextNode(s); }
  function slug(s) { return String(s).toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, ""); }
  function gapD(ref, reason) {
    return { v: null, prov: "gap", ref: ref || undefined, reason: reason || (ref && D.gaps[ref] ? D.gaps[ref].reason : "not in the sources") };
  }
  function fd(key) {
    var f = F[key];
    if (!f) throw new Error("No figure " + key + " in RBOT_DATA.figures");
    return { v: f.v, prov: f.prov, ref: f.ref, reason: f.reason };
  }
  /* a figure's presented value (filings' parentheses) wins over the raw record value */
  var FIG_BY_REF = {};
  Object.keys(F).forEach(function (k) { var f = F[k]; if (f.ref && !(f.ref in FIG_BY_REF)) FIG_BY_REF[f.ref] = f.v; });
  function refDatum(ref) {
    var c = D.citations[ref];
    if (c) return { v: ref in FIG_BY_REF ? FIG_BY_REF[ref] : c.value, prov: c.synthetic ? "synthetic" : "cited", ref: ref };
    var k = D.calcs[ref];
    if (k) return { v: k.value, prov: "calculated", ref: ref };
    if (D.gaps[ref]) return gapD(ref);
    throw new Error("Unknown reference " + ref);
  }
  /* rich("text {K55|x} more [G8]"): {REF} prints the record's value with its chip, [REF] a chip alone */
  var TOKEN = /\{([CKGS]\d+)(?:\|([^}]*))?\}|\[([CKGS]\d+)\]/g;
  function rich(str) {
    var out = [], last = 0, m;
    TOKEN.lastIndex = 0;
    while ((m = TOKEN.exec(str))) {
      if (m.index > last) out.push(txt(str.slice(last, m.index)));
      if (m[1]) out.push(UI.value(refDatum(m[1]), m[2] || undefined));
      else { refDatum(m[3]); out.push(UI.chip(m[3])); }
      last = TOKEN.lastIndex;
    }
    if (last < str.length) out.push(txt(str.slice(last)));
    return out;
  }
  function refsIn(str) {
    var out = [], m;
    TOKEN.lastIndex = 0;
    while ((m = TOKEN.exec(str))) { var r = m[1] || m[3]; if (out.indexOf(r) < 0) out.push(r); }
    return out;
  }
  /* tokens by figure key: tk prints the value and its chip, ck the chip alone */
  function tk(key, unit) { if (!F[key]) throw new Error("No figure " + key); return "{" + F[key].ref + (unit ? "|" + unit : "") + "}"; }
  function ck(key) { if (!F[key]) throw new Error("No figure " + key); return "[" + F[key].ref + "]"; }
  /* Model-authored, illustrative prose: dotted underline, Model tag, ILLUSTRATIVE tag */
  function authored(nodes, opts) {
    var span = el("span", { class: "prov-model" }, nodes);
    return [span, opts && opts.noTag ? null : el("span", { class: "tag-model", text: "Model" }), UI.illus()];
  }
  function itemNodes(item) {
    var kids = [el("span", { class: "prov-model", text: item.text })];
    (item.refs || []).forEach(function (r) { kids.push(UI.chip(r)); });
    return kids;
  }
  /* margin notes: the citations a prose block rests on, as an IC paper's side notes */
  function notes(refs) {
    var ol = el("ol", { class: "mnotes", "aria-label": "Sources for this passage" });
    refs.forEach(function (r) {
      var c = D.citations[r], k = D.calcs[r], g = D.gaps[r], src, label, val;
      if (c) { label = c.label; val = c.value; src = c.file + ", " + (c.locator || "line " + c.line); }
      else if (k) { label = k.label; val = k.value; src = k.formula; }
      else if (g) { label = "Not in the sources"; val = null; src = g.reason; }
      else return;
      ol.appendChild(el("li", {}, [UI.chip(r), el("span", {}, [el("b", { text: label }), val ? txt(": " + val) : null]),
        el("span", { class: "mnotes__src", text: src })]));
    });
    return ol;
  }
  function annot(nodes, refs) {
    return el("div", { class: "annot" }, [el("div", { class: "annot__text" }, nodes), notes(refs)]);
  }
  function isIllus(node, what) {
    return el("span", { class: "is-illus", title: what + ": illustrative, no RBOT run exists" }, [node, el("span", { class: "vh", text: " (illustrative)" })]);
  }
  function dirChip(word) {
    var w = String(word).toLowerCase();
    var cls = /improving|positive/.test(w) ? "up" : /deteriorating|negative/.test(w) ? "down" : "flat";
    return el("span", { class: "dir dir--" + cls, text: word });
  }
  function scaleRec(r, label, size) { return UI.scale({ kind: "rec", pos: r.pos, word: r.word, illustrative: true, label: label, size: size }); }

  /* ------------------------------------------------------------ tables */
  function th(label, unit, num) {
    return el("th", { scope: "col", class: num ? "num" : null }, [label, unit ? el("span", { class: "unit", text: unit }) : null]);
  }
  function tdD(d, opts) {
    var c = el("td", { class: opts && opts.text ? null : "num" });
    UI.cell(c, d, opts && opts.unit);
    return c;
  }
  function nowrap(td) { td.classList.add("nowrap"); return td; }
  function tdN(nodes, cls) { return el("td", { class: cls || null }, nodes); }
  function rowTh(label, cls) { return el("th", { scope: "row", class: cls || null, text: label }); }
  function table(caption, cols, rows, cls) {
    var t = el("table", { class: "dt " + (cls || "") }, [
      caption ? el("caption", { class: "vh", text: caption }) : null,
      el("thead", {}, [el("tr", {}, cols)]),
      el("tbody", {}, rows)
    ]);
    return el("div", { class: "table-scroll" }, [t]);
  }
  function kindClass(k) { return k === "total" ? "total" : k === "sub" ? "sub" : k === "indent" ? "indent" : null; }
  function periodTable(t, filter, caption, cls) {
    var cols = [th(t.unit || "")].concat(t.columns.map(function (c) { return th(c, null, true); }));
    var rows = t.rows.filter(filter || function () { return true; }).map(function (r) {
      var row = el("tr", { class: kindClass(r.kind) }, [rowTh(r.label)]);
      r.cells.forEach(function (d) { row.appendChild(tdD(d)); });
      return row;
    });
    return table(caption || t.title, cols, rows, "pt" + (cls ? " " + cls : ""));
  }
  function pick(t, labels) { return function (r) { return labels.indexOf(r.label) >= 0; }; }
  function kvTable(caption, pairs) {
    return el("table", { class: "dt dt--kv" }, [el("caption", { class: "vh", text: caption }),
      el("tbody", {}, pairs.map(function (p) { return el("tr", {}, [rowTh(p[0]), el("td", {}, p[1])]); }))]);
  }
  function srcNote(text, nodes) { return el("p", { class: "chart__source pad" }, nodes || [txt(text)]); }

  /* ------------------------------------------------------------ figures (numbered per view, captioned) */
  function draw(kind, host, spec, over) {
    figN += 1;
    var sp = Object.assign({}, spec, { number: "Figure " + figN, headingLevel: 4 }, over || {});
    var base = sp.id || ("fig-" + figN);
    sp.id = curView + "--" + base;
    figs[curView + "|" + base] = { n: figN, id: sp.id };
    charts.push(C[kind](host, sp));
    return figN;
  }
  /* A figure the data cannot draw: the frame, its title and the missing input with its reason. */
  function naFigure(host, o) {
    figN += 1;
    var id = curView + "--" + o.id;
    figs[curView + "|" + o.id] = { n: figN, id: id };
    var reasons = el("span", {}, []);
    o.refs.forEach(function (r) { reasons.appendChild(UI.chip(r)); });
    host.appendChild(el("figure", { class: "chart chart--na", id: id }, [
      el("div", { class: "chart__head" }, [el("span", { class: "chart__num", text: "Figure " + figN }),
        el("h4", { class: "chart__title", text: o.title }), el("p", { class: "chart__summary", text: o.summary })]),
      el("div", { class: "chart__plot", role: "img", "aria-label": o.title + ": not drawn, " + o.missing }, [
        el("p", { class: "chart__na" }, [el("b", { text: "n/a: not drawn" }), txt(o.missing + " "), reasons])]),
      el("p", { class: "chart__source", text: "Source: " + o.source })
    ]));
  }
  function figHost(parent) { var h = el("div", { class: "figbox" }); parent.appendChild(h); return h; }

  /* ------------------------------------------------------------ collapsible blocks */
  /* One affordance everywhere: a bar with a chevron, the title, tags and, when a module owns the block,
     a "Full analysis" link. The state is also written in words ("Collapse" / "Expand"). */
  function cb(parent, o) {
    var tags = [];
    if (o.illus) tags.push(UI.illus());
    if (o.synth) tags.push(el("span", { class: "synth", text: "Synthetic" }));
    if (o.model) tags.push(el("span", { class: "tag-model", text: "Model" }));
    var head = el("summary", {}, [
      el("h" + (o.level || 2), { class: "cb__t", id: o.id ? o.id + "-h" : null }, [o.title]),
      el("span", { class: "cb__meta" }, o.meta || []),
      tags.length ? el("span", { class: o.paper ? "cb__tags" : "cb__tags on-navy" }, tags) : null,
      o.full ? el("a", { class: "cb__full", href: o.full, "aria-label": "Full analysis of " + o.title }, ["Full analysis"]) : null
    ]);
    var body = el("div", { class: "cb__body" + (o.flush ? " cb__body--flush" : "") });
    var d = el("details", { class: "cb " + (o.paper ? "cb--paper " : "") + (o.cls || ""), id: o.id || null }, [head, body]);
    d.open = o.open !== false;
    parent.appendChild(d);
    return body;
  }
  function viewTools(v) {
    var b = el("button", { type: "button", class: "btn btn--quiet vtools", text: "Collapse all sections" });
    function sync() {
      var all = v.el.querySelectorAll("details.cb");
      var any = Array.prototype.some.call(all, function (d) { return d.open; });
      b.textContent = any ? "Collapse all sections" : "Expand all sections";
    }
    b.addEventListener("click", function () {
      var all = v.el.querySelectorAll("details.cb"), any = Array.prototype.some.call(all, function (d) { return d.open; });
      Array.prototype.forEach.call(all, function (d) { d.open = !any; });
      sync();
    });
    v.el.addEventListener("toggle", sync, true);
    return b;
  }

  /* ------------------------------------------------------------ views */
  function newView(id, o) {
    curView = id; figN = 0;
    var h1 = el("h1", { class: "vtitle", tabindex: "-1" }, o.h1 || o.title);
    var v = { id: id, title: o.title, group: o.group || null, el: null, h1: h1, nav: null };
    v.el = el("article", { class: "view" + (o.cls ? " " + o.cls : ""), id: "view-" + id, "data-view": id, "aria-labelledby": "view-" + id + "-h" });
    h1.id = "view-" + id + "-h";
    v.el.hidden = true;
    VIEWS[id] = v; ORDER.push(id);
    main.appendChild(v.el);
    return v;
  }
  function plainHead(v, lede, aside) {
    var top = el("div", { class: "vhead__top" }, [v.h1, aside || null]);
    var hd = el("header", { class: "vhead" }, [top, lede ? el("p", { class: "vhead__lede" }, lede) : null]);
    v.el.appendChild(hd);
    v.tools = viewTools(v);
    top.appendChild(v.tools);
    return hd;
  }

  /* ================================================================ 1. CREDIT SNAPSHOT (summary screen) */
  var MODS = D.modules;
  var TOPIC_OF_ID = { "CP-0": "intake", "CP-1": "financials", "CP-1A": "business", "CP-1B": "delta", "CP-1D": "quality", "CP-2": "fundamentals",
    "CP-2A": "downside", "CP-3": "rv", "CP-4": "legal", "CP-5": "qa" };
  var HOST = { business: "financials", quality: "financials", downside: "fundamentals", fit: "rv", challenge: "downside" };
  function topicOf(m) {
    if (TOPIC_OF_ID[m.id]) return TOPIC_OF_ID[m.id];
    if (/portfolio|fit/i.test(m.name)) return "fit";
    if (/challenge|committee/i.test(m.name)) return "challenge";
    return null;
  }
  var OWNED = {};
  MODS.forEach(function (m) { var t = topicOf(m); if (t) OWNED[t] = m; });
  function hostOf(topic) { return OWNED[topic] || (HOST[topic] && hostOf(HOST[topic])) || null; }
  function modId(m) { return "module-" + slug(m.id); }
  /* "Full analysis" target: the section of the module view that owns a topic */
  function fullLink(topic, part) {
    var m = hostOf(topic);
    return m ? "#" + (part ? slug(m.id) + "-" + part : modId(m)) : null;
  }

  function opmParagraphs() {
    var seg = function (s) { return tk("opm_seg_rev_" + s + "_fy2025", "US$ m"); };
    var share = function (s) { return tk("opm_seg_share_" + s + "_fy2025"); };
    var p = [
      "Caesars is a " + tk("opm_description") + ", founded in " + tk("opm_founded") + ". Its primary source of revenue is " + tk("opm_revenue_source") + ".",
      "It reports " + tk("opm_segments_count") + ": Las Vegas, Regional, Caesars Digital, and Managed and Branded. FY2025 net revenues of " + tk("net_revenues_fy2025", "US$ m") +
        " came from Regional at " + seg("regional") + " (" + share("regional").replace("}", "|%}") + " of the total), Las Vegas at " + seg("las_vegas") + " (" + share("las_vegas").replace("}", "|%}") +
        "), Caesars Digital at " + seg("caesars_digital") + " and Managed and Branded at " + seg("managed_branded") + ", which earns " + tk("opm_mb_fees") +
        " for managing other hotels and casinos. By type, casino was approximately " + tk("opm_casino_share_fy2025", "%") + " of net revenues, hotel " + tk("opm_hotel_share_fy2025", "%") +
        " and food and beverage " + tk("opm_fb_share_fy2025", "%") + ".",
      "At 30 June 2026 it owned, leased or managed " + tk("opm_properties") + " properties in " + tk("opm_jurisdictions") + " jurisdictions. It owned " + tk("opm_owned_casinos") +
        " of its casinos and leased " + tk("opm_leased_casinos") + ": " + tk("opm_vici_casinos") + " from VICI, " + tk("opm_glpi_casinos") + " from GLPI and Caesars Windsor from the " + tk("opm_windsor") +
        ". The VICI and GLPI leases are financing obligations of " + tk("opm_vici_obligation") + " and " + tk("opm_glpi_obligation") + " at 31 December 2025, and " +
        tk("lt_financing_obligations_2026_06_30", "US$ m") + " at 30 June 2026, shown apart from reported debt.",
      "Caesars Digital operates sports wagering across " + tk("opm_sports_jurisdictions") + " jurisdictions, " + tk("opm_online_sports_jurisdictions") + " of them online, and iGaming in " +
        tk("opm_igaming_jurisdictions") + ". On " + tk("issuer.merger.agreement_date") + " Fertitta Entertainment agreed to acquire Caesars for " + tk("merger_price_per_share_pr") +
        " per share in cash, a transaction valued at " + tk("merger_transaction_value", "US$ bn") + " including assumed debt of " + tk("merger_assumed_debt", "US$ bn") + "."
    ];
    return p.map(function (s) { return el("p", { class: "desc__p" }, [el("span", { class: "prov-model" }, rich(s))]); });
  }
  function kpiStrip() {
    var items = [["opm_properties", "Properties"], ["opm_jurisdictions", "Jurisdictions"], ["opm_slots", "Slots, VLTs, e-tables"], ["opm_tables", "Table games"],
      ["opm_rooms", "Hotel rooms"], ["opm_owned_casinos", "Casinos owned"], ["opm_leased_casinos", "Casinos leased"]];
    return el("dl", { class: "kpis", "aria-label": "Property footprint at 30 June 2026" }, items.map(function (x) {
      return el("div", { class: "kpis__i" }, [el("dt", { text: x[1] }), el("dd", {}, [UI.value(fd(x[0]))])]);
    }));
  }

  function buildSnapshot() {
    var v = newView("snapshot", { title: "Snapshot", h1: "Credit Snapshot: " + M.issuer, cls: "view--snapshot" });
    var s = v.el;

    /* title band: the call */
    var meta = el("p", { class: "titleband__meta" }, [
      el("span", { text: M.pathway + ", " + M.depth + " depth" }),
      M.primary ? el("span", { text: M.primaryLabel }) : null,
      el("span", { text: M.reportingPeriod }),
      el("span", { text: "Analysis " + M.analysisDate }),
      el("span", { text: M.runId ? "Run " + M.runId : M.runNote })
    ]);
    var call = el("div", { class: "call on-navy", role: "group", "aria-label": "Analyst recommendation, illustrative" }, [
      el("div", { class: "call__label" }, [el("span", { class: "call__title" }, ["Analyst recommendation", UI.illus()]),
        el("span", { class: "call__who" }, [txt("Analyst " + M.analyst.v + " · Date "), el("span", { class: "num", text: M.analysisDate })])])
    ]);
    M.strategies.forEach(function (st) {
      call.appendChild(el("span", { class: "call__item" }, [el("span", { class: "call__k", text: st }), scaleRec(I.recommendation[st], st, "lg")]));
    });
    call.appendChild(el("span", { class: "call__rule", "aria-hidden": "true" }));
    call.appendChild(el("span", { class: "call__item" }, [el("span", { class: "call__k", text: "Valuation" }),
      UI.scale({ kind: "val", pos: I.valuation.pos, illustrative: true, label: "Valuation", size: "lg" })]));
    call.appendChild(el("span", { class: "call__item" }, [el("span", { class: "call__k", text: "Credit Score" }),
      UI.scale({ kind: "score", pos: I.creditScore.pos, word: I.creditScore.word, illustrative: true, label: "Credit Score", size: "lg" })]));
    s.appendChild(el("header", { class: "titleband" }, [
      el("div", { class: "titleband__top" }, [v.h1, v.tools = viewTools(v)]),
      meta, call
    ]));

    var fp = el("div", { class: "fp" });
    s.appendChild(fp);

    /* Key findings and the main risk */
    var kf = cb(fp, { title: "Key findings", id: "key-findings", cls: "span-12 p-kf", illus: true, flush: true });
    kf.appendChild(el("ol", { class: "kf" }, I.keyFindings.map(function (f) { return el("li", {}, [el("span", {}, itemNodes(f))]); })));
    var risk = I.weaknesses[0];
    kf.appendChild(el("p", { class: "kf__thesis" }, [el("b", { text: "Main risk: " + risk.label + ". " })].concat(itemNodes(risk))));

    /* Company description with the operating model: what Caesars does and how it makes money */
    var co = cb(fp, { title: "Company description and operating model", id: "company", cls: "span-12 p-co", model: true, full: fullLink("business", "business"),
      meta: ["Every figure cited from the FY2025 10-K and the Q2 2026 10-Q"] });
    var paras = opmParagraphs();
    co.appendChild(el("div", { class: "co" }, [
      el("div", { class: "co__text" }, [paras[0], paras[1]]),
      el("div", { class: "co__side" }, [
        el("h3", { class: "co__h", text: "Segments, FY2025" }),
        periodTable(OM.segments, null, null, "wraphead"),
        srcNote(OM.segments.note)
      ])
    ]));
    co.appendChild(el("div", { class: "co co--more" }, [el("div", { class: "co__text" }, [paras[2]]), el("div", { class: "co__text" }, [paras[3]])]));
    co.appendChild(kpiStrip());

    /* Figures 1-4: the Model chart strip and the debt maturity wall */
    var fb = cb(fp, { title: "Model chart strip", id: "figures", cls: "span-12 p-figs", flush: true, full: "#model",
      meta: ["Figures 1 to 4. Select any mark for its source"] });
    var row = el("div", { class: "figrow" });
    fb.appendChild(row);
    [["lineStrip", K.leverage], ["lineStrip", K.coverage], ["lineStrip", K.liquidity], ["stackedColumns", K.maturityWall]].forEach(function (p) {
      var cell = el("div", { class: "figcell" });
      row.appendChild(cell);
      draw(p[0], cell, p[1], { height: 112, ticks: 3 });
    });

    /* Capital structure summary | EBITDA adjustments summary */
    var cap = cb(fp, { title: "Capital structure", id: "capital-structure", cls: "span-7 p-cap", flush: true, full: fullLink("financials", "capital-structure"),
      meta: ["At " + T.capitalStructure.asOf + "; x LTM Adjusted EBITDA"] });
    cap.appendChild(capSummary());
    cap.appendChild(srcNote("", rich("EBITDA basis: " + T.capitalStructure.ebitda_basis + ". Financing obligations to GLPI and VICI of {C184} are shown apart from debt.")));
    var adj = cb(fp, { title: "EBITDA adjustments", id: "ebitda-adjustments", cls: "span-5 p-adj", flush: true, full: fullLink("financials", "quality"),
      meta: [T.ebitdaAdjustments.unit] });
    adj.appendChild(periodTable(T.ebitdaAdjustments));
    adj.appendChild(srcNote(T.ebitdaAdjustments.note));

    /* Financials summary: key rows, credit metrics and the revenue and EBITDA chart */
    var fin = cb(fp, { title: "Financials and credit metrics", id: "financials", cls: "span-12 p-fin", flush: true, full: fullLink("financials", "financials"),
      meta: [T.financials.unit + " (metrics in x); negatives in parentheses as filed"] });
    var fg = el("div", { class: "finbox" });
    fin.appendChild(fg);
    var fl = el("div", { class: "finbox__tables" });
    fg.appendChild(fl);
    fl.appendChild(periodTable(T.financials, pick(T.financials, ["Revenue", "EBITDA (Adjusted, company-defined)", "% margin", "FCF"]), "Financials summary"));
    fl.appendChild(periodTable(T.creditMetrics, pick(T.creditMetrics, ["Total Leverage", "Net Leverage", "Interest Cover"]), "Credit metrics summary"));
    var fr = el("div", { class: "finbox__chart" });
    fg.appendChild(fr);
    draw("columns", fr, K.revenueEbitda, { height: 170 });

    /* Strengths and weaknesses */
    var sw = cb(fp, { title: "Strengths and weaknesses", id: "credit-summary", cls: "span-12 p-sw", illus: true, flush: true, full: fullLink("rv", "credit-view") });
    sw.appendChild(el("p", { class: "sw__thesis" }, [el("b", { text: "Thesis. " })].concat(itemNodes(I.thesis))));
    sw.appendChild(el("div", { class: "swgrid" }, [
      el("div", {}, [el("div", { class: "bar bar--sub", text: "Strengths" }), swRows(I.strengths)]),
      el("div", {}, [el("div", { class: "bar bar--sub", text: "Weaknesses" }), swRows(I.weaknesses)])
    ]));

    /* Relative value summary */
    var rv = cb(fp, { title: "Relative value", id: "rv-summary", cls: "span-12 p-rv", flush: true, open: false, full: fullLink("rv"),
      meta: ["Bonds on TRACE, 2 October 2026; spreads, loan marks and index statistics are n/a"] });
    rv.appendChild(rvSummary());

    /* Company profile (the template's identifiers, ratings and outlooks) */
    var prof = cb(fp, { title: "Company profile", id: "company-profile", cls: "span-12 p-prof", flush: true, open: false, full: fullLink("intake", "profile"),
      meta: [el("span", { class: "is-illus is-illus--key" }, ["dashed"]), " = illustrative"] });
    prof.appendChild(profileTable());

    /* Transaction summary (Primary runs only) */
    if (M.primary) {
      var tx = cb(fp, { title: "Transaction summary and new debt issues", id: "transaction", cls: "span-12 p-tx", flush: true, open: false, full: fullLink("business", "business"),
        meta: [M.primaryLabel] });
      tx.appendChild(el("div", { class: "tx__text" }, [el("p", {}, itemNodes(I.transactionSummary).concat([UI.illus()]))]));
      tx.appendChild(newDebtTable());
    }
  }

  function swRows(list) {
    return el("table", { class: "dt sw" }, [el("tbody", {}, list.map(function (w) {
      return el("tr", {}, [rowTh(w.label), el("td", {}, itemNodes(w))]);
    }))]);
  }
  function profileTable() {
    var cells = [
      ["Ticker", [UI.value(fd("issuer.ticker"))]],
      ["Management", [txt("CEO "), UI.value(fd("issuer.ceo")), txt(", CFO "), UI.value(fd("issuer.cfo"))]],
      ["Credit Score", [isIllus(UI.scale({ kind: "score", pos: I.creditScore.pos, word: I.creditScore.word, illustrative: true, label: "Credit Score" }), "Credit Score")]],
      ["Morningstar Issuer ID", [UI.value(gapD("G24"))]],
      ["Sector Outlook", [isIllus(dirChip(I.sectorOutlook.word), "Sector Outlook")]],
      ["Credit Direction", [isIllus(dirChip(I.creditDirection.word), "Credit Direction")]],
      ["Sector / Country", [UI.value(gapD(null, "sector and country of domicile are not among the extracted figures"))]],
      ["Sponsor Quality", [isIllus(el("span", { class: "prov-model", title: I.sponsorQuality.basis, text: I.sponsorQuality.word }), "Sponsor Quality")]],
      ["Issue ratings (M/S)", [txt("SS 2032s "), UI.value(fd("trace_czr_12769gac4_moodys")), txt(" / "), UI.value(fd("trace_czr_12769gac4_sp"))]],
      ["Shareholders", [txt("Listed; merger agreed with Fertitta"), UI.chip(F["issuer.merger.acquirer_brand"].ref)]],
      ["Corp Ratings (M/S/F)", [UI.value(gapD("G25")), txt(" / Fitch "), UI.value(gapD("G10"))]],
      ["Outlook (M/S/F)", [UI.value(gapD("G11"))]]
    ];
    var pbody = el("tbody");
    for (var ci = 0; ci < cells.length; ci += 3) {
      var tr = el("tr");
      cells.slice(ci, ci + 3).forEach(function (c) { tr.appendChild(rowTh(c[0])); tr.appendChild(el("td", {}, c[1])); });
      pbody.appendChild(tr);
    }
    return el("div", { class: "table-scroll" }, [el("table", { class: "dt dt--kv kv3" }, [el("caption", { class: "vh", text: "Company profile" }), pbody])]);
  }
  function newDebtTable() {
    var g8 = gapD("G8");
    return table("New debt issues", [th("Borrower"), th("Bloomberg ID (FIGI)"), th("Instrument"), th("Debt type"), th("UoP"),
      th("Tranche size", "US$ m", true), th("Guidance / IPT"), th("OID"), th("Maturity"), th("Exp. ratings"), th("CR Score"), th("Commit date")], [
      el("tr", {}, [tdD(g8, { text: true }), tdD(gapD("G28"), { text: true }),
        tdN([txt("New debt from "), UI.value(fd("merger_financing_banks_count")), txt(" banks")], "nowrap"), tdD(g8, { text: true }),
        tdN([isIllus(el("span", { class: "prov-model", text: "Acquisition" }), "Use of proceeds"), UI.chip("C12")], "nowrap"),
        tdD(g8), tdD(g8, { text: true }), tdD(g8), tdD(g8, { text: true }), tdD(g8, { text: true }), tdD(g8, { text: true }), tdD(g8, { text: true })])
    ], "wraphead");
  }

  /* capital structure: the full facility table (module view) and a subtotal summary (Snapshot) */
  function rankLabel(rank) { return rank === "secured" ? "Senior secured debt" : rank === "unsecured" ? "Unsecured debt" : "Other debt"; }
  function rankAmount(rank, sub) { return rank === "secured" ? sub.senior_secured : rank === "unsecured" ? sub.unsecured : sub.other; }
  function capSummary() {
    var cs = T.capitalStructure, sub = cs.subtotals, rows = [];
    function line(label, amount, last, cls, extra) {
      rows.push(el("tr", { class: cls || null }, [rowTh(label), tdD(amount), last ? tdD(last.ssim_multiple) : (extra ? tdD(extra) : el("td")), last ? tdD(last.pct_ev) : el("td")]));
    }
    ["secured", "unsecured", "other"].forEach(function (rank) {
      var rs = cs.rows.filter(function (r) { return r.rank === rank; });
      if (rs.length) line(rankLabel(rank) + " (" + rs.length + (rs.length === 1 ? " facility" : " facilities") + ")", rankAmount(rank, sub), rs[rs.length - 1], "total");
    });
    line("Total debt", sub.total_debt, cs.rows[cs.rows.length - 1], "total");
    line("Cash", sub.cash, null, "sub");
    line("Net debt", sub.net_debt, null, "sub");
    rows.push(el("tr", { class: "total" }, [rowTh("EV (merger transaction value) and EV multiple"), tdD(sub.ev), tdD(sub.ev_multiple), el("td")]));
    return table("Capital structure summary at " + cs.asOf, [th("Debt"), th("Outstanding", "US$ m", true), th("Cumulative multiple", "x", true), th("% EV", "%", true)], rows, "capsum");
  }
  function capitalTable() {
    var cs = T.capitalStructure, sub = cs.subtotals;
    var recs = {};
    I.byInstrument.forEach(function (r) { recs[r.facility] = r; });
    var cols = [th("Facility"), th("Bloomberg ID (FIGI)"), th("Facility ratings", "M / S"), th("Spread / coupon", "%", true), th("CCY"), th("Maturity"),
      th("Bid", null, true), th("Ask", null, true), th("Outstanding", "US$ m", true), th("Structuring multiple", "x", true), th("SSIM multiple", "x", true),
      th("% EV", "%", true), el("th", { scope: "col" }, ["Recommendation", el("span", { class: "unit" }, [UI.illus()])])];
    var rows = [];
    function facility(r) {
      var rec = recs[r.facility];
      var bid = tdD(r.bid), ask = tdD(r.ask);
      if (r.price_note) { bid.title = r.price_note; ask.title = r.price_note; }
      rows.push(el("tr", { class: "indent" }, [rowTh(r.facility), tdD(r.figi, { text: true }), tdD(r.ratings, { text: true }), tdD(r.coupon),
        el("td", { text: r.ccy }), tdD(r.maturity, { text: true }), bid, ask, tdD(r.outstanding), tdD(r.structuring_multiple), tdD(r.ssim_multiple), tdD(r.pct_ev),
        tdN([rec ? UI.scale({ kind: "rec", pos: rec.pos, word: rec.word, illustrative: true, label: r.facility }) : UI.value(gapD(null, "no instrument recommendation"))])]));
    }
    function subtotal(label, amount, lastRow, cls) {
      rows.push(el("tr", { class: cls || "total" }, [el("th", { scope: "row", colspan: "8", style: "text-align:right", text: label }), tdD(amount),
        lastRow ? tdD(lastRow.structuring_multiple) : el("td"), lastRow ? tdD(lastRow.ssim_multiple) : el("td"), lastRow ? tdD(lastRow.pct_ev) : el("td"), el("td")]));
    }
    ["secured", "unsecured", "other"].forEach(function (rank) {
      var rs = cs.rows.filter(function (r) { return r.rank === rank; });
      if (!rs.length) return;
      rs.forEach(facility);
      subtotal(rankLabel(rank), rankAmount(rank, sub), rs[rs.length - 1], "total");
    });
    subtotal("Total debt", sub.total_debt, cs.rows[cs.rows.length - 1], "total");
    subtotal("Cash", sub.cash, null, "sub");
    subtotal("Net debt", sub.net_debt, null, "sub");
    subtotal("(Implied) equity, at the merger value", sub.implied_equity, null, "sub");
    rows.push(el("tr", { class: "total" }, [el("th", { scope: "row", colspan: "8", style: "text-align:right", text: "EV (merger transaction value) and EV multiple" }),
      tdD(sub.ev), tdD(sub.ev_multiple), el("td"), el("td"), el("td")]));
    rows.push(el("tr", { class: "sub" }, [el("th", { scope: "row", colspan: "8", style: "text-align:right", text: "Equity market value" }), tdD(sub.equity_market_value), el("td"), el("td"), el("td"), el("td")]));
    rows.push(el("tr", { class: "sub" }, [el("th", { scope: "row", colspan: "8", style: "text-align:right", text: "PF interest" }), tdD(sub.pf_interest), el("td"), el("td"), el("td"), el("td")]));
    return table("Capital structure at " + cs.asOf, cols, rows, "captab wraphead");
  }

  var INDEX_GAP = "Bloomberg index statistics are not in the Source Pack";
  function rvSummary() {
    var g19 = gapD("G19");
    var sizes = { "12769GAC4": "CEI 6.50% Senior Secured Notes 2032", "12769GAD2": "CEI 6.00% Senior Notes 2032" };
    var capBy = {};
    T.capitalStructure.rows.forEach(function (r) { capBy[r.facility] = r; });
    return table("Comparable bonds, summary", [th("Company"), th("CUSIP"), th("Seniority"), th("Coupon", "%", true), th("Maturity"), th("Size", "US$ m", true),
      th("Last price", null, true), th("Last yield", "%", true), th("OAS", "bp", true)], T.trace.rows.map(function (r) {
      var capRow = capBy[sizes[r.cusip]];
      return el("tr", {}, [rowTh(r.issuer), el("td", { class: "num", text: r.cusip }), nowrap(el("td", { text: r.seniority })), tdD(r.coupon), tdD(r.maturity, { text: true }),
        tdD(capRow ? capRow.outstanding : gapD(null, "peer issue size is not among the extracted figures")), tdD(r.price), tdD(r.yield), tdD(g19)]);
    }), "wraphead");
  }
  function loanRv() {
    var wrap = el("div");
    wrap.appendChild(table("Loan index statistics", [th("Index rating bucket"), th("Bloomberg ID"), th("Market value", "US$ bn", true), th("Avg price", null, true),
      th("Δ 1M", null, true), th("Δ YTD", null, true), th("YTM", "%", true), th("3Y DM", "bp", true)], [
      el("tr", {}, [rowTh("Ba · Ba/B · B · Caa"), el("td", { colspan: "7" }, [UI.value(gapD(null, INDEX_GAP))])])
    ]));
    var g18 = gapD("G18");
    var loans = T.capitalStructure.rows.filter(function (r) { return /Term Loan/.test(r.debtType); });
    wrap.appendChild(table("Comparable loans", [th("Company"), th("Facility"), th("FIGI"), th("Ratings"), th("Size", "US$ m", true), th("Margin", "bp", true),
      th("Maturity"), th("Seniority"), th("Mid", null, true), th("Δ 1M", null, true), th("Δ YTD", null, true), th("Mid YTM", "%", true), th("Mid 3Y DM", "bp", true)],
      loans.map(function (r) {
        return el("tr", {}, [rowTh(M.ticker), el("td", { text: r.facility }), tdD(r.figi, { text: true }), tdD(r.ratings, { text: true }), tdD(r.outstanding), tdD(g18),
          tdD(r.maturity, { text: true }), el("td", { text: r.debtType }), tdD(g18), tdD(g18), tdD(g18), tdD(g18), tdD(g18)]);
      }).concat([el("tr", { class: "sub" }, [el("th", { scope: "row", colspan: "13" }, [txt("Peer loans: "), UI.value(gapD("G18"))])])]), "wraphead"));
    return wrap;
  }
  function hyRv() {
    var wrap = el("div");
    wrap.appendChild(table("High-yield index statistics", [th("Index rating bucket"), th("Bloomberg ID"), th("Avg coupon", "%", true), th("Market value", "US$ bn", true),
      th("Avg price", null, true), th("Δ 1M", null, true), th("Δ YTD", null, true), th("YTW", "%", true), th("OAS", "bp", true)], [
      el("tr", {}, [rowTh("Ba · Ba/B · B · Caa"), el("td", { colspan: "8" }, [UI.value(gapD(null, INDEX_GAP))])])
    ]));
    var sizes = { "12769GAC4": "CEI 6.50% Senior Secured Notes 2032", "12769GAD2": "CEI 6.00% Senior Notes 2032" };
    var capBy = {};
    T.capitalStructure.rows.forEach(function (r) { capBy[r.facility] = r; });
    var g19 = gapD("G19"), noHist = gapD(null, "price history is not in the sources; TRACE pages give the last trade only");
    wrap.appendChild(table("Comparable bonds", [th("Company"), th("CUSIP"), th("FIGI"), th("Moody's"), th("S&P"), th("Size", "US$ m", true), th("Coupon", "%", true),
      th("Maturity"), th("Next call"), th("Seniority"), th("Last price", null, true), th("Δ 1M", null, true), th("Δ YTD", null, true), th("Last yield", "%", true), th("OAS", "bp", true)],
      T.trace.rows.map(function (r) {
        var capRow = capBy[sizes[r.cusip]];
        return el("tr", {}, [rowTh(r.issuer), el("td", { class: "num", text: r.cusip }), tdD(gapD("G28"), { text: true }),
          tdD(r.moodys, { text: true }), tdD(r.sp, { text: true }), tdD(capRow ? capRow.outstanding : gapD(null, "peer issue size is not among the extracted figures")),
          tdD(r.coupon), tdD(r.maturity, { text: true }), tdD(r.next_call, { text: true }), nowrap(el("td", { text: r.seniority })), tdD(r.price), tdD(noHist), tdD(noHist),
          tdD(r.yield), tdD(g19)]);
      }), "wraphead"));
    return wrap;
  }

  /* ================================================================ 2. MODULE VIEWS */
  function docs() {
    var by = {};
    Object.keys(D.citations).forEach(function (id) { var c = D.citations[id]; by[c.file] = (by[c.file] || 0) + 1; });
    return Object.keys(by).map(function (f) { return { file: f, n: by[f], synthetic: /Test_CLO/.test(f) }; });
  }
  function gapTable(refs, caption) {
    return table(caption, [th("Gap"), th("Field"), th("Reason")], refs.map(function (r) {
      var g = D.gaps[r];
      return el("tr", {}, [el("th", { scope: "row" }, [UI.chip(r)]), el("td", { text: g.field }), el("td", { text: g.reason })]);
    }));
  }
  /* label / value / as-at rows, every value a cited or calculated figure */
  function figKv(caption, keys, withPeriod) {
    return el("div", { class: "table-scroll" }, [el("table", { class: "dt dt--kv dt--framed" }, [el("caption", { class: "vh", text: caption }), el("tbody", {}, keys.map(function (k) {
      return el("tr", {}, [rowTh(F[k].label.charAt(0).toUpperCase() + F[k].label.slice(1)), el("td", {}, [UI.value(fd(k))]),
        withPeriod ? el("td", { class: "kv__when", text: F[k].period || "" }) : null]);
    }))])]);
  }
  function rowsTable(t) {
    return table(t.title, [th(t.title), th(t.unit, null, true)], t.rows.map(function (r, i, a) {
      return el("tr", { class: i === a.length - 1 && /total/i.test(r.label) ? "total" : null }, [rowTh(r.label), tdD(r.cell)]);
    }), "dt--framed");
  }
  function docTable() {
    return table("Documents admitted", [th("Document"), th("Citations", null, true), th("Kind")], docs().map(function (d) {
      return el("tr", {}, [el("th", { scope: "row", text: d.file }), el("td", { class: "num", text: String(d.n) }),
        el("td", {}, d.synthetic ? [el("span", { class: "synth", text: "Synthetic" })] : [txt(/TRACE/.test(d.file) ? "Market levels" : /^(MGM|PENN)/.test(d.file) ? "Peer filing" : "Issuer filing")])]);
    }));
  }
  function scoresTable() {
    return kvTable("Scores and valuation", [
      ["Credit Score", [UI.scale({ kind: "score", pos: I.creditScore.pos, word: I.creditScore.word, illustrative: true, label: "Credit Score" }), UI.illus()]],
      ["Valuation", [UI.scale({ kind: "val", pos: I.valuation.pos, illustrative: true, label: "Valuation" }), UI.illus()]],
      ["Credit Direction", [dirChip(I.creditDirection.word), UI.illus()]],
      ["Sector Outlook", [dirChip(I.sectorOutlook.word), UI.illus()]],
      ["Sponsor Quality", [el("span", { class: "prov-model", text: I.sponsorQuality.word + ". " + I.sponsorQuality.basis }), UI.illus()]]
    ].concat(M.strategies.map(function (st) { return [st, [scaleRec(I.recommendation[st], st), UI.illus()]]; })));
  }

  /* operating model in full: the content of the business section of CP-1 */
  function operatingModelFull(body) {
    opmParagraphs().forEach(function (p) { body.appendChild(p); });
    body.appendChild(kpiStrip());
    body.appendChild(el("h4", { text: "Segments, FY2025" }));
    body.appendChild(periodTable(OM.segments, null, null, "wraphead"));
    body.appendChild(srcNote(OM.segments.note));
    var pair = el("div", { class: "figpair" });
    body.appendChild(pair);
    var a = figHost(pair), b = figHost(pair);
    a.appendChild(el("h4", { text: "Net revenues by type" }));
    a.appendChild(periodTable(OM.revenueType, null, null, "wraphead"));
    draw("stackedColumns", b, K.segmentMix, { height: 230 });
    body.appendChild(srcNote("", [txt(K.segmentMix.note)]));
    var two = el("div", { class: "figpair" });
    body.appendChild(two);
    var re = figHost(two), dg = figHost(two);
    re.appendChild(el("h4", { text: "Owned versus leased real estate" }));
    re.appendChild(figKv("Owned versus leased real estate", ["opm_owned_casinos", "opm_leased_casinos", "opm_vici_casinos", "opm_glpi_casinos", "opm_windsor",
      "opm_vici_term", "opm_vici_rent", "opm_vici_obligation", "opm_glpi_term", "opm_glpi_obligation", "lt_financing_obligations_2026_06_30"], true));
    dg.appendChild(el("h4", { text: "Digital" }));
    dg.appendChild(figKv("Digital footprint", ["opm_sports_jurisdictions", "opm_online_sports_jurisdictions", "opm_igaming_jurisdictions", "opm_racebook_states"], true));
    body.appendChild(el("p", { class: "na-note", text: "Not stated in the filings as a count and so left out: properties per segment (the 10-K lists them by name), and the owned or leased status of each property by segment." }));
  }

  /* Topics carry the content; modules from RBOT_DATA decide which topics get their own view.
     A topic whose module is not in this run's module list joins its host module's view. */
  var TOPICS = {
    intake: {
      title: "Intake and readiness", ledeTitle: "Gaps raised at intake", detailTitle: "Documents admitted",
      headline: function () {
        var n = docs().filter(function (d) { return !d.synthetic; }).length;
        return n + " issuer, market and peer documents are admitted; the merger's debt commitment terms [G8], a Fitch rating [G10] and rating outlooks [G11] are not in the Source Pack.";
      },
      lede: function (host, m) { host.appendChild(gapTable(m && m.refs && m.refs.length ? m.refs : ["G8", "G10", "G11"], "Gaps raised at intake")); },
      detail: function (body) { body.appendChild(docTable()); }
    },
    financials: {
      title: "Financial analysis and capital structure", ledeTitle: "Debt stack", detailTitle: "Credit metrics and balance sheet",
      headline: "LTM Adjusted EBITDA of {K2} on net revenues of {K1}; total debt of {C114} puts total leverage at {K55|x} and net leverage at {K56|x}, before any merger debt [G8].",
      lede: function (host) {
        var sub = T.capitalStructure.subtotals;
        draw("waterfall", host, {
          id: "fig-debt-stack", title: "Debt stack by rank, 30 June 2026", unit: "US$ m", categoryLabel: "Rank",
          summary: "Senior secured " + sub.senior_secured.v + ", unsecured " + sub.unsecured.v + " and other " + sub.other.v + " make total debt of " + sub.total_debt.v + " at face value.",
          steps: [{ label: "Senior secured debt", short: "Secured", kind: "total", d: sub.senior_secured },
            { label: "Unsecured debt", short: "Unsecured", kind: "delta", d: sub.unsecured },
            { label: "Other debt", short: "Other", kind: "delta", d: sub.other },
            { label: "Total debt, face value", short: "Total debt", kind: "total", d: sub.total_debt }],
          source: "Caesars Q2 2026 10-Q debt table; subtotals by build-data.py"
        }, { height: 200 });
      },
      detail: function (body) {
        body.appendChild(periodTable(T.creditMetrics));
        body.appendChild(el("p", { class: "na-note", text: T.creditMetrics.note }));
        body.appendChild(periodTable(T.balanceSheet));
      }
    },
    business: {
      title: "Business and operating model",
      headline: "Fertitta Entertainment agreed on {C11} to acquire Caesars for {C210} per share in cash, a transaction valued at {C212|US$ bn} including assumed debt of {C213|US$ bn}; the new debt has no stated amount [G8].",
      lede: null,
      detail: function (body) {
        operatingModelFull(body);
        body.appendChild(el("h4", { text: "Merger terms" }));
        body.appendChild(figKv("Merger terms", ["issuer.merger.acquirer_brand", "issuer.merger.parent", "issuer.merger.parent_guarantor", "issuer.merger.agreement_date",
          "merger_price_per_share_pr", "merger_transaction_value", "merger_assumed_debt", "merger_premium_unaffected", "merger_premium_vwap", "issuer.merger.financing",
          "issuer.merger.financing_condition", "merger_go_shop_end", "merger_initial_end_date", "issuer.merger.caesars_advisors", "issuer.merger.fertitta_advisors"]));
        if (M.primary) {
          body.appendChild(el("h4", { text: "Transaction summary and new debt issues" }));
          body.appendChild(el("p", {}, itemNodes(I.transactionSummary).concat([UI.illus()])));
          body.appendChild(newDebtTable());
        }
        body.appendChild(el("h4", { text: "Segments, Q2 2026 against Q2 2025" }));
        body.appendChild(periodTable(T.segments));
        body.appendChild(el("h4", { text: "Catalysts and near-term events" }));
        body.appendChild(el("table", { class: "dt" }, [el("caption", { class: "vh", text: "Catalysts" }), el("tbody", {}, I.catalysts.map(function (c) {
          return el("tr", {}, [el("td", {}, itemNodes(c).concat([UI.illus()]))]);
        }))]));
      }
    },
    delta: {
      title: "Earnings delta", ledeTitle: "Segment change, Q2 2026 against Q2 2025", detailTitle: "Segments table",
      headline: "Q2 2026 against Q2 2025: Regional Adjusted EBITDA rose to {C96} from {C97} while Las Vegas fell to {C94} from {C95}; the cash side of the delta is available for six months only [G3].",
      lede: function (host) { draw("dumbbell", host, K.segments); },
      detail: function (body) { body.appendChild(periodTable(T.segments)); }
    },
    quality: {
      title: "Earnings quality", ledeTitle: "Adjusted EBITDA bridge", detailTitle: "EBITDA adjustments",
      headline: "Q2 2026 Adjusted EBITDA of {K66} reconciles from a net loss of {C192}; the add-backs are transaction costs of {C204} and stock-based compensation of {C206}, and none is unrealized [G22].",
      lede: function (host) { draw("waterfall", host, K.ebitdaBridge, { height: 230 }); },
      detail: function (body) { body.appendChild(periodTable(T.ebitdaAdjustments)); body.appendChild(el("p", { class: "na-note", text: T.ebitdaAdjustments.note })); }
    },
    fundamentals: {
      title: "Fundamentals, liquidity and cash flow", ledeTitle: "Cash bridge", detailTitle: "Interest path, liquidity and maturities",
      headline: "Cash and revolver capacity of {C177} at 30 June 2026 against {C178} of debt due in the rest of 2026; H1 2026 free cash flow of {K44} after capex of {C45}.",
      lede: function (host) { draw("waterfall", host, K.cashBridge, { height: 220 }); },
      detail: function (body) {
        var pair = el("div", { class: "figpair" });
        body.appendChild(pair);
        var a = figHost(pair), b = figHost(pair);
        draw("lineStrip", a, K.interestPath, { height: 190 });
        naFigure(b, { id: "fig-liquidity-bridge", title: "Liquidity bridge, 12 months", summary: "Beginning to ending accessible liquidity over the next twelve months.",
          missing: "Needs twelve-month sources and uses: quarterly cash flows, H1 investing and financing flows, and a company forecast are not in the sources.",
          refs: ["G3", "G26", "G13"], source: "Caesars Q2 2026 10-Q; no forecast in the Source Pack" });
        var two = el("div", { class: "figpair" });
        body.appendChild(two);
        two.appendChild(rowsTable(T.liquidity));
        two.appendChild(rowsTable(T.maturities));
      }
    },
    downside: {
      title: "Downside", ledeTitle: "Risk matrix", detailTitle: "Risk register",
      headline: "Two events sit in the high zone: the merger's new debt of unstated size [G8] and the Las Vegas trend, where Adjusted EBITDA fell to {C94} from {C95}.",
      lede: function (host) { draw("riskMatrix", host, K.risk); },
      detail: function (body) {
        body.appendChild(table("Risk register", [th("Event"), th("Description"), th("Probability"), th("Impact"), th("Classification")], K.risk.events.map(function (e) {
          return el("tr", {}, [rowTh(e.key + " " + e.label), el("td", {}, [el("span", { class: "prov-model", text: e.description }), e.ref ? UI.chip(e.ref) : null, UI.illus()]),
            el("td", { text: e.probability }), el("td", { text: e.impact }), el("td", { text: e.classification })]);
        })));
      }
    },
    rv: {
      title: "Relative value", ledeTitle: "Yield against maturity", detailTitle: "Peer range, scores and valuation",
      headline: "The secured 2032s last traded at {C232} to yield {C233|%} and the unsecured 2032s at {C241} to yield {C242|%}, against {C251|%} and {C260|%} for the MGM and PENN 2029s; spreads are not in the sources [G19].",
      lede: function (host) { draw("scatter", host, K.yieldCurve, { height: 230 }); },
      detail: function (body) {
        var pair = el("div", { class: "figpair" });
        body.appendChild(pair);
        draw("rangeStrip", figHost(pair), K.peerRange);
        var v = figHost(pair);
        v.appendChild(el("h4", { text: "Scores and valuation" }));
        v.appendChild(scoresTable());
        body.appendChild(el("p", { class: "na-note", text: K.peerRange.note }));
      }
    },
    legal: {
      title: "Legal and covenants", ledeTitle: "Covenant headroom", detailTitle: "Merger agreement protections and missing documents",
      headline: "No maintenance covenant level is cited [G17], so headroom is not drawn against net leverage of {K56|x}; the merger agreement carries a reverse termination fee of US$ {C226} and an End Date of {C220}.",
      lede: function (host) { draw("bullet", host, K.covenant); },
      detail: function (body) {
        body.appendChild(figKv("Merger agreement protections", ["issuer.merger.financing_condition", "merger_termination_fee", "merger_termination_fee_reduced",
          "merger_reverse_termination_fee", "merger_initial_end_date", "merger_first_extended_end_date", "merger_second_extended_end_date", "merger_ticking_fee_date", "merger_ticking_fee_per_day"]));
        body.appendChild(gapTable(["G17", "G8"], "Legal documents not in the sources"));
      }
    },
    qa: {
      title: "Evidence QA", ledeTitle: "Evidence counts", detailTitle: "Reconciliations",
      headline: function () {
        return "Every figure carries a citation or a formula; total debt by facility sums to {K60} against a stated {C114}, and the H1 2026 cash bridge leaves {K67} unexplained by the extracted lines [G26].";
      },
      lede: function (host) {
        var c = D.counts;
        host.appendChild(table("Evidence counts", [th("Record"), th("Count", null, true), th("Opens to")], [
          el("tr", {}, [rowTh("Cited figures"), el("td", { class: "num", text: String(c.cited) }), el("td", { text: "file, line, verbatim excerpt" })]),
          el("tr", {}, [rowTh("Calculated figures"), el("td", { class: "num", text: String(c.calculated) }), el("td", { text: "formula and its cited inputs" })]),
          el("tr", {}, [rowTh("Logged gaps"), el("td", { class: "num", text: String(c.gaps) }), el("td", { text: "field and reason" })]),
          el("tr", {}, [rowTh("Synthetic portfolio rows"), el("td", { class: "num", text: String(c.synthetic_sources) }), el("td", { text: "Test CLO I file and row" })])
        ]));
      },
      detail: function (body) {
        body.appendChild(table("Reconciliations", [th("Check"), th("Stated", null, true), th("Calculated", null, true), th("Note")], [
          el("tr", {}, [rowTh("Total debt by facility"), tdD(refDatum("C114")), tdD(refDatum("K60")), el("td", { text: "The facility rows sum to the stated total." })]),
          el("tr", {}, [rowTh("Q2 2026 Adjusted EBITDA bridge"), tdD(fd("recon_adj_ebitda_q2_2026")), tdD(refDatum("K66")), el("td", {}, [txt("Net loss to Adjusted EBITDA reconciles; see the earnings-quality section of "), el("a", { href: "#" + slug(hostOf("quality") ? hostOf("quality").id : "CP-1") + "-quality", text: "its module" })])]),
          el("tr", {}, [rowTh("H1 2026 cash bridge"), tdD(refDatum("C104")), tdD(refDatum("K67")), el("td", {}, [txt("Residual unexplained by the extracted lines; see the cash bridge in "), el("a", { href: "#" + (hostOf("fundamentals") ? modId(hostOf("fundamentals")) : "snapshot"), text: "its module" })])])
        ]));
      }
    },
    fit: {
      title: "Portfolio Fit", ledeTitle: "Sector weights", detailTitle: "Checks",
      headline: function () { return P.fit.summary; },
      synthetic: true,
      lede: function (host) { draw("rangeStrip", host, K.cloSectors); },
      detail: function (body) {
        body.appendChild(el("p", {}, [txt("The checks, per-instrument fit and the Test CLO I constraint schedule are in the "), el("a", { href: "#portfolio-fit", text: "Portfolio Fit view" }), txt(".")]));
      }
    },
    challenge: {
      title: "Committee challenge", ledeTitle: "Challenges", detailTitle: "Responses",
      headline: "Would the secured 2032s hold value if the merger adds debt of unknown size [G8], and is the fall in Las Vegas Adjusted EBITDA to {C94} from {C95} cyclical or structural?",
      lede: function (host) {
        host.appendChild(table("Challenges", [th("Challenge"), th("Rests on")], I.weaknesses.map(function (w) {
          return el("tr", {}, [rowTh(w.label), el("td", {}, itemNodes(w).concat([UI.illus()]))]);
        })));
      },
      detail: function (body) { body.appendChild(el("p", { class: "na-note", text: "Responses to each challenge would come from the run; none exists for this mockup." })); }
    }
  };
  function headlineNodes(t, m) {
    var str = typeof t.headline === "function" ? t.headline(m) : t.headline;
    var nodes = authored(rich(str));
    if (t.synthetic) nodes.push(el("span", { class: "synth", text: "Synthetic" }));
    return { nodes: nodes, refs: refsIn(str) };
  }

  /* extra sections a module view carries beyond its figure, tables and sources */
  var EXTRAS = {
    financials: function (v, sid, add) {
      add({ key: "capital-structure", title: "Capital structure", meta: ["At " + T.capitalStructure.asOf + "; multiples are cumulative, x LTM Adjusted EBITDA"], flush: true }, function (b) {
        b.appendChild(capitalTable());
        b.appendChild(srcNote("", rich("EBITDA basis: " + T.capitalStructure.ebitda_basis + ". Financing obligations to GLPI and VICI of {C184} are shown in the balance sheet, not added to debt.")));
      });
      add({ key: "financials", title: "Financials", meta: [T.financials.unit + "; negatives in parentheses as filed"], flush: true }, function (b) { b.appendChild(periodTable(T.financials)); });
      add({ key: "history", title: "Historical performance", illus: true }, function (b) {
        b.appendChild(el("p", {}, itemNodes(I.historicalPerformance)));
        draw("columns", figHost(b), K.revenueEbitda, { height: 200 });
      });
    },
    rv: function (v, sid, add) {
      add({ key: "credit-view", title: "Credit view: thesis, strengths and weaknesses", illus: true }, function (b) {
        b.appendChild(annot([el("p", {}, itemNodes(I.thesis))], I.thesis.refs));
        b.appendChild(el("div", { class: "swgrid" }, [
          el("div", {}, [el("div", { class: "bar bar--sub", text: "Strengths" }), swRows(I.strengths)]),
          el("div", {}, [el("div", { class: "bar bar--sub", text: "Weaknesses" }), swRows(I.weaknesses)])
        ]));
      });
      add({ key: "loan-rv", title: "Loan relative value", meta: ["Index: Bloomberg US Leveraged Loan Index"], flush: true }, function (b) { b.appendChild(loanRv()); });
      add({ key: "hy-rv", title: "High-yield relative value", meta: ["Index: Bloomberg US Corporate High Yield Index; bonds: " + T.trace.title], flush: true }, function (b) { b.appendChild(hyRv()); });
    },
    intake: function (v, sid, add) {
      add({ key: "profile", title: "Company profile", illus: true, flush: true, open: false }, function (b) { b.appendChild(profileTable()); });
    }
  };

  function buildModule(m, i) {
    var id = modId(m), sid = slug(m.id), t = topicOf(m), topic = t ? TOPICS[t] : null;
    var v = newView(id, { title: m.name, group: "Analysis", h1: m.name, cls: "view--module" });
    v.mod = m; v.code = m.id;
    var hd = plainHead(v, null, null);
    hd.insertBefore(el("p", { class: "vhead__crumb" }, [el("span", { text: "Analysis" }), el("span", { class: "vhead__code", text: m.id })]), hd.firstChild);
    var facts = el("div", { class: "vfacts" });
    hd.appendChild(facts);
    facts.appendChild(el("div", { class: "vfact" }, [el("span", { class: "vfact__k", text: "Reader question" }), el("p", { class: "vfact__v", text: m.question })]));
    var st = el("p", { class: "vfact__v" }, [el("b", { text: m.status + ". " }), txt(m.reason + " ")]);
    (m.refs || []).forEach(function (r) { st.appendChild(UI.chip(r)); });
    facts.appendChild(el("div", { class: "vfact" }, [el("span", { class: "vfact__k" }, ["Status ", UI.status(m.status)]), st]));
    var hl = topic ? headlineNodes(topic, m) : null;
    if (hl) hd.appendChild(el("div", { class: "headline" }, [el("span", { class: "headline__k", text: "Headline finding" }), el("p", { class: "headline__v" }, hl.nodes)]));
    else hd.appendChild(el("p", { class: "na-note", text: "No headline finding is written for this module." }));

    var n = 0;
    function add(o, build) {
      n += 1;
      var body = cb(v.el, { title: o.title, id: o.key ? sid + "-" + o.key : null, paper: true, level: 2, meta: o.meta, illus: o.illus, synth: o.synth, flush: o.flush, open: o.open });
      build(body);
    }
    if (topic && topic.lede) add({ key: "figure", title: topic.ledeTitle || "Figures" }, function (b) { topic.lede(b, m); });
    if (topic && topic.detail) add({ key: "detail", title: topic.detailTitle || "Detailed tables" }, function (b) { topic.detail(b, m); });
    if (t && EXTRAS[t]) EXTRAS[t](v, sid, add);
    /* topics with no module of their own join this one */
    Object.keys(HOST).forEach(function (sub) {
      if (hostOf(sub) !== m || OWNED[sub] || sub === t) return;
      var tp = TOPICS[sub], h2 = headlineNodes(tp);
      add({ key: sub, title: tp.title }, function (b) {
        b.appendChild(el("p", { class: "lede-line" }, h2.nodes));
        if (tp.lede) tp.lede(figHost(b));
        if (tp.detail) tp.detail(b);
        b.appendChild(el("div", { class: "src-notes" }, [el("h4", { text: "Sources for this finding" }), notes(h2.refs)]));
      });
    });
    /* findings with their citations */
    add({ key: "findings", title: "Findings and sources" }, function (b) {
      if (hl) b.appendChild(el("div", { class: "src-notes" }, [el("h4", { text: "Sources for the headline finding" }), notes(hl.refs)]));
      if (t === "financials") {
        b.appendChild(el("h4", { text: "Key findings" }));
        b.appendChild(el("ol", { class: "kf kf--one" }, I.keyFindings.map(function (f) { return el("li", {}, [el("span", {}, itemNodes(f).concat([UI.illus()]))]); })));
      }
      if (!hl && !(t === "financials")) b.appendChild(el("p", { class: "na-note", text: "No findings are written for this module." }));
    });
    /* its gaps and limitations */
    add({ key: "gaps", title: "Gaps and limitations" }, function (b) {
      var refs = (m.refs || []).filter(function (r) { return D.gaps[r]; });
      b.appendChild(el("p", {}, [el("b", { text: "Why " + m.status + ". " }), txt(m.reason)]));
      if (refs.length) b.appendChild(gapTable(refs, "Gaps raised against " + m.id));
      else b.appendChild(el("p", { class: "na-note", text: "No gap is raised against this module. The run-wide limitations are on the Limitations view." }));
    });
    /* previous and next */
    var prev = i > 0 ? { href: "#" + modId(MODS[i - 1]), k: "Previous module", t: MODS[i - 1].id + "  " + MODS[i - 1].name } : { href: "#snapshot", k: "Back to", t: "Snapshot" };
    var next = i < MODS.length - 1 ? { href: "#" + modId(MODS[i + 1]), k: "Next module", t: MODS[i + 1].id + "  " + MODS[i + 1].name } : { href: "#model", k: "Next view", t: "Model" };
    v.el.appendChild(el("nav", { class: "pager", "aria-label": "Previous and next module" }, [
      el("a", { class: "pager__a pager__a--prev", href: prev.href }, [el("span", { class: "pager__k", text: prev.k }), el("span", { class: "pager__t", text: prev.t })]),
      el("a", { class: "pager__a pager__a--next", href: next.href }, [el("span", { class: "pager__k", text: next.k }), el("span", { class: "pager__t", text: next.t })])
    ]));
  }

  /* ================================================================ 3. MODEL */
  function buildModel() {
    var v = newView("model", { title: "Model" });
    plainHead(v, ["Values-only twin of model.xlsx. Select any cell for its passport: source, locator, excerpt or formula."]);
    var fin = T.financials;
    var earningsRows = function (r) { return fin.rows.indexOf(r) <= 5; };
    var cashRows = function (r) { return fin.rows.indexOf(r) >= 6; };
    var bands = [
      { id: "model-earnings", t: "Earnings", lede: "LTM net revenues {K1} and Adjusted EBITDA {K2}, a margin of {K47|%}; FY2023 Adjusted EBITDA was {C74}.",
        fig: function (h) { draw("columns", h, K.revenueEbitda, { height: 190 }); }, body: function (b) { b.appendChild(periodTable(fin, earningsRows, "Earnings")); } },
      { id: "model-ebitda-bridge", t: "Adjusted EBITDA bridge", lede: "Q2 2026 Reported EBITDA {K65} plus transaction costs {C204} and stock-based compensation {C206} gives Structuring EBITDA {K66}; SSIM equals Structuring [G22].",
        fig: function (h) { draw("waterfall", h, K.ebitdaBridge, { height: 230 }); }, body: function (b) { b.appendChild(periodTable(T.ebitdaAdjustments)); b.appendChild(el("p", { class: "na-note", text: T.ebitdaAdjustments.note })); } },
      { id: "model-cash-flow", t: "Cash flow waterfall", lede: "LTM cash from operations {K4} less capex {K3} leaves free cash flow of {K50}; lease cash interest of {K9} runs through rent.",
        fig: function (h) { draw("waterfall", h, K.cashBridge, { height: 220 }); }, body: function (b) { b.appendChild(periodTable(fin, cashRows, "Cash flow")); } },
      { id: "model-debt-stack", t: "Debt stack by rank", lede: "Senior secured {K57}, unsecured {K58} and other {K59}: total debt {C114} at face; financing obligations of {C184} are shown apart from debt.",
        fig: function (h) { TOPICS.financials.lede(h); }, body: function (b) { b.appendChild(debtStack()); } },
      { id: "model-credit-metrics", t: "Credit metrics", lede: "Total leverage {K55|x}, net {K56|x} and senior {K61|x}; interest cover {K51|x}, or {K52|x} on debt cash interest alone.",
        fig: function (h) { draw("lineStrip", h, K.leverage, { height: 170 }); }, body: function (b) { b.appendChild(periodTable(T.creditMetrics)); b.appendChild(periodTable(T.balanceSheet)); } }
    ];
    bands.forEach(function (bd, i) {
      var body = cb(v.el, { title: bd.t, id: bd.id, paper: true, open: i < 2 });
      body.appendChild(el("p", { class: "band__text" }, rich(bd.lede)));
      bd.fig(figHost(body));
      bd.body(body);
    });
  }
  function debtStack() {
    var cs = T.capitalStructure;
    var rows = [];
    ["secured", "unsecured", "other"].forEach(function (rank) {
      cs.rows.filter(function (r) { return r.rank === rank; }).forEach(function (r) {
        rows.push(el("tr", {}, [rowTh(r.facility), el("td", { text: rank }), el("td", { text: r.debtType }), tdD(r.outstanding), tdD(r.book), tdD(r.structuring_multiple), tdD(r.pct_ev)]));
      });
    });
    rows.push(el("tr", { class: "total" }, [rowTh("Total debt"), el("td"), el("td"), tdD(cs.subtotals.total_debt), el("td"), el("td"), el("td")]));
    return table("Debt stack by rank", [th("Facility"), th("Rank"), th("Debt type"), th("Face", "US$ m", true), th("Book", "US$ m", true), th("Cumulative multiple", "x", true), th("% EV", "%", true)], rows);
  }

  /* ================================================================ 4. PORTFOLIO FIT */
  function buildFit() {
    var fit = P.fit;
    var v = newView("portfolio-fit", { title: "Portfolio Fit", h1: "Portfolio Fit: " + P.name });
    plainHead(v, [el("span", { class: "synth", text: "Synthetic" }), " ", UI.illus(), " Portfolio as of " + P.asOf + ". The mandate, holdings and limits are synthetic Test CLO I files."]);
    var body = cb(v.el, { title: "Fit checks", id: "portfolio-fit-checks", paper: true, synth: true, illus: true });
    var grid = el("div", { class: "pf-summary" });
    body.appendChild(grid);
    var left = el("div"), right = el("div");
    grid.appendChild(left); grid.appendChild(right);
    left.appendChild(el("div", { class: "pf-verdict" }, [el("h3", { text: "Portfolio Fit" }), UI.status(fit.overall.v), UI.illus()]));
    left.appendChild(el("p", {}, [el("span", { class: "prov-model", text: fit.summary }), el("span", { class: "tag-model", text: "Model" })]));
    left.appendChild(table("Fit checks", [th("Constraint"), th("Limit"), th("Current", null, true), th("Headroom", null, true), th("Result")], fit.checks.map(function (c) {
      return el("tr", {}, [el("th", { scope: "row" }, [txt(c.constraint), UI.chip(c.ref)]), nowrap(el("td", { text: c.limit })), el("td", { class: "num", text: c.current }),
        el("td", { class: "num", text: c.headroom }), el("td", {}, [UI.status(c.result), c.note ? el("div", { class: "gap__reason", text: c.note }) : null])]);
    })));
    draw("bullet", right, K.cloLimits);
    var inst = cb(v.el, { title: "Fit by instrument", id: "portfolio-fit-instrument", paper: true, synth: true, illus: true });
    inst.appendChild(table("Fit by instrument", [th("Instrument"), th("Fit"), th("Note")], fit.byInstrument.map(function (b) {
      return el("tr", {}, [rowTh(b.instrument), el("td", {}, [UI.status(b.fit)]), el("td", { text: b.note || "" })]);
    })));
    var det = cb(v.el, { title: "Test CLO I: constraints, summary, mandate and sectors", id: "portfolio-fit-detail", paper: true, synth: true, open: false });
    det.appendChild(el("h4", { text: "Constraint schedule" }));
    det.appendChild(table("Constraints", [th("ID"), th("Category"), th("Parameter"), th("Limit"), th("Type"), th("Current", null, true), th("Headroom", null, true), th("Status"), th("Source")],
      P.constraints.map(function (c) {
        return el("tr", {}, [el("th", { scope: "row" }, [txt(c.id), UI.chip(c.ref)]), el("td", { text: c.category }), el("td", { text: c.parameter }), el("td", { text: c.limit }),
          el("td", { text: c.breachType }), el("td", { class: "num", text: c.current }), el("td", { class: "num", text: c.headroom }), el("td", {}, [UI.status(c.status)]), el("td", { text: c.sourceDocument })]);
      })));
    var pair = el("div", { class: "figpair", style: "margin-top: var(--s-4)" });
    det.appendChild(pair);
    function kvd(obj, cap) {
      return el("table", { class: "dt dt--kv dt--framed" }, [el("caption", { text: cap }), el("tbody", {}, Object.keys(obj).map(function (k) {
        var c = el("td"); UI.cell(c, obj[k]);
        return el("tr", {}, [rowTh(k), c]);
      }))]);
    }
    pair.appendChild(kvd(P.summary, "Portfolio summary"));
    pair.appendChild(kvd(P.mandate, "Mandate"));
    det.appendChild(el("h4", { style: "margin-top: var(--s-4)", text: "Sector weights" }));
    det.appendChild(table("Sectors", [th("Sector"), th("% NAV", null, true), th("Issuers", null, true), th("Limit"), th("Headroom", null, true), th("Status")],
      P.sectors.map(function (x) {
        return el("tr", {}, [rowTh(x.sector), el("td", { class: "num", text: x.pct }), el("td", { class: "num", text: x.issuers }), el("td", { text: x.limit }),
          el("td", { class: "num", text: x.headroom }), el("td", {}, [UI.status(x.status)])]);
      })));
  }

  /* ================================================================ 5. EVIDENCE */
  function buildEvidence() {
    var c = D.counts;
    var v = newView("evidence", { title: "Evidence" });
    plainHead(v, ["Every citation with its verbatim excerpt, every calculation with its formula and inputs: " + c.cited + " cited, " + c.calculated + " calculated, " + c.gaps + " gaps, " + c.synthetic_sources + " synthetic."]);
    cb(v.el, { title: "Documents admitted", id: "evidence-documents", paper: true }).appendChild(docTable());
    var cites = Object.keys(D.citations).filter(function (k) { return !D.citations[k].synthetic; });
    var synth = Object.keys(D.citations).filter(function (k) { return D.citations[k].synthetic; });
    function citeRows(ids) {
      return ids.map(function (id) {
        var x = D.citations[id];
        return el("tr", {}, [el("th", { scope: "row" }, [UI.chip(id)]), el("td", { text: x.label }), el("td", { class: "num", text: x.value }),
          el("td", { text: x.period || "" }), el("td", { text: x.file }), el("td", { text: x.locator || "" }), el("td", { class: "ex", text: x.excerpt })]);
      });
    }
    var citeCols = function () { return [th("ID"), th("Figure"), th("Value", null, true), th("Period"), th("File"), th("Locator"), th("Excerpt")]; };
    [["evidence-citations", "Citations (" + cites.length + ")", function () { return tall(table("Citations", citeCols(), citeRows(cites), "evid")); }],
     ["evidence-calcs", "Calculations (" + Object.keys(D.calcs).length + ")", function () {
       return tall(table("Calculations", [th("ID"), th("Figure"), th("Period"), th("Value", null, true), th("Formula"), th("Inputs")], Object.keys(D.calcs).map(function (id) {
         var k = D.calcs[id], ins = el("td");
         (k.inputs || []).forEach(function (r) { ins.appendChild(UI.chip(r)); });
         return el("tr", {}, [el("th", { scope: "row" }, [UI.chip(id)]), el("td", { text: k.label }), el("td", { text: k.period || "" }), el("td", { class: "num", text: k.value }),
           el("td", {}, [el("code", { text: k.formula })]), ins]);
       }), "evid"));
     }],
     ["evidence-synthetic", "Synthetic portfolio rows (" + synth.length + ")", function () { return tall(table("Synthetic rows", citeCols(), citeRows(synth), "evid")); }]
    ].forEach(function (x) {
      cb(v.el, { title: x[1], id: x[0], paper: true, open: false, flush: true }).appendChild(x[2]());
    });
  }
  function tall(node) { node.classList.add("tall-scroll"); return node; }

  /* ================================================================ 6. LIMITATIONS */
  function buildLimitations() {
    var L = D.limitations;
    var byScope = {};
    L.forEach(function (l) { byScope[l.scope] = (byScope[l.scope] || 0) + 1; });
    var v = newView("limitations", { title: "Limitations" });
    plainHead(v, ["Stated before the run and carried into the Report. " + L.length + " known at Approval: " + Object.keys(byScope).map(function (k) { return k + ": " + byScope[k]; }).join(" · ") + "."]);
    var model = L.filter(function (l) { return /^Model limitation/.test(l.scope); });
    function limRows(list) {
      return list.map(function (l) {
        return el("tr", {}, [el("th", { scope: "row" }, [UI.chip(l.ref)]), el("td", { text: l.field }), el("td", { text: l.text }), el("td", { text: l.scope }), el("td", { text: l.origin })]);
      });
    }
    var cols = function () { return [th("Gap"), th("Field"), th("Limitation"), th("Scope"), th("Origin")]; };
    var b1 = cb(v.el, { title: "Model limitations", id: "limitations-known", paper: true });
    if (model.length) {
      b1.appendChild(el("p", { text: "These limit the Model itself:" }));
      b1.appendChild(table("Model limitations", cols(), limRows(model)));
    } else b1.appendChild(el("p", { class: "na-note", text: "No limitation of the Model itself is recorded." }));
    cb(v.el, { title: "All " + L.length + " limitations known at Approval", id: "limitations-all", paper: true, open: false, flush: true })
      .appendChild(table("Limitations known at Approval", cols(), limRows(L)));
    var b2 = cb(v.el, { title: "Unforeseen", id: "limitations-unforeseen", paper: true });
    var U = D.unforeseen || [];
    if (U.length) b2.appendChild(table("Unforeseen limitations", cols(), limRows(U)));
    else b2.appendChild(el("p", { text: "None recorded. No RBOT run exists, so nothing arose after Approval." }));
  }

  /* ================================================================ navigation pane */
  function buildNav() {
    var nav = document.getElementById("nav");
    var ul = el("ul", { class: "nav__list" });
    function link(id, label, code, status) {
      var a = el("a", { class: "nav__a", href: "#" + id, "data-view": id }, [
        code ? el("span", { class: "nav__code", text: code }) : null,
        el("span", { class: "nav__t", text: label }),
        status ? el("span", { class: "on-navy nav__st" }, [UI.status(status)]) : null
      ]);
      VIEWS[id].nav = a;
      return el("li", {}, [a]);
    }
    ul.appendChild(link("snapshot", "Snapshot"));
    var tally = {};
    MODS.forEach(function (m) { tally[m.status] = (tally[m.status] || 0) + 1; });
    var grp = el("li", { class: "nav__grp" }, [
      el("span", { class: "nav__gt", id: "nav-analysis-h", text: "Analysis" }),
      el("span", { class: "nav__gm", text: MODS.length + " modules: " + Object.keys(tally).map(function (k) { return tally[k] + " " + k; }).join(", ") }),
      el("ul", { "aria-labelledby": "nav-analysis-h" }, MODS.map(function (m) { return link(modId(m), m.name, m.id, m.status); }))
    ]);
    ul.appendChild(grp);
    ["model", "portfolio-fit", "evidence", "limitations"].forEach(function (id) { ul.appendChild(link(id, VIEWS[id].title)); });
    nav.appendChild(ul);
    document.getElementById("pane-issuer").textContent = M.issuer.replace(/, Inc\.$/, "") + " (" + M.ticker + ")";
    document.getElementById("pane-meta").textContent = M.pathway + " · " + M.reportingPeriod + " · Analysis " + M.analysisDate;
  }

  /* ================================================================ router */
  var ALIASES = { "analysis": null, "paper": "snapshot" };
  var activeId = null;
  var menu = document.getElementById("pane-menu"), sheet = document.getElementById("pane-sheet");
  function sheetOpen(open) {
    menu.setAttribute("aria-expanded", String(open));
    document.getElementById("pane").classList.toggle("is-open", open);
  }
  function viewTitle(v) { return (v.code ? v.code + " " : "") + v.title; }
  function show(v, user) {
    if (activeId === v.id) return;
    if (activeId) { VIEWS[activeId].el.hidden = true; if (VIEWS[activeId].nav) VIEWS[activeId].nav.removeAttribute("aria-current"); }
    activeId = v.id;
    v.el.hidden = false;
    if (v.nav) { v.nav.setAttribute("aria-current", "page"); }
    document.title = viewTitle(v) + " · Credit Snapshot: " + M.issuer + " (" + M.ticker + "), RBOT Report";
    document.getElementById("pane-where").textContent = viewTitle(v);
    document.getElementById("route-live").textContent = viewTitle(v);
    window.scrollTo(0, 0);
    if (user) v.h1.focus({ preventScroll: true });
    charts.forEach(function (c) { c.redraw(); });
    if (v.nav && v.nav.scrollIntoView) { var r = v.nav.getBoundingClientRect(); var pr = document.getElementById("pane-sheet").getBoundingClientRect(); if (r.top < pr.top || r.bottom > pr.bottom) v.nav.scrollIntoView({ block: "nearest" }); }
  }
  /* open every closed section around the target, then bring it into view */
  function reveal(t) {
    for (var p = t; p; p = p.parentElement) if (p.tagName === "DETAILS") p.open = true;
    if (t.tagName === "DETAILS") t.open = true;
    requestAnimationFrame(function () { t.scrollIntoView({ block: "start" }); });
  }
  function route(user) {
    var id = decodeURIComponent(location.hash.replace(/^#/, ""));
    var target = null, v = VIEWS[id];
    if (!v && id in ALIASES) v = VIEWS[ALIASES[id] || modId(MODS[0])];
    if (!v && id) {
      target = document.getElementById(id);
      var owner = target && target.closest ? target.closest(".view") : null;
      v = owner ? VIEWS[owner.getAttribute("data-view")] : null;
    }
    if (!v) v = VIEWS.snapshot;
    show(v, user);
    if (target) reveal(target);
    sheetOpen(false);
  }

  /* ================================================================ print */
  /* Print: the Snapshot is re-flowed into a grid and scaled to fit one landscape page; every view
     after it prints with every section open. */
  var PAGE_W = 985, PAGE_H = 712;   /* CSS px inside @page margins; fits both US Letter and A4 landscape */
  var wasOpen = null;
  function printPrepare() {
    if (wasOpen) return;
    var root = document.documentElement, snap = VIEWS.snapshot.el;
    wasOpen = [];
    document.querySelectorAll("details").forEach(function (d) { wasOpen.push([d, d.open]); d.open = true; });
    UI.close(false);
    root.classList.add("printing");
    function settle(V) {
      snap.style.width = V + "px"; snap.style.zoom = "1";
      charts.forEach(function (c) { c.redraw(); });
      var r0 = snap.getBoundingClientRect(), z = Math.min(PAGE_W / r0.width, PAGE_H / r0.height);
      for (var k = 0; k < 5; k++) {
        snap.style.zoom = String(Math.floor(z * 1000) / 1000);
        var r = snap.getBoundingClientRect();
        if (r.height <= PAGE_H && r.width <= PAGE_W) break;
        z = z * Math.min(PAGE_H / r.height, PAGE_W / r.width) * 0.995;
      }
      return Math.floor(z * 1000) / 1000;
    }
    var best = null;
    [1700, 2000, 2300, 2600].forEach(function (V) { var z = settle(V); if (!best || z > best.z) best = { V: V, z: z }; });
    settle(best.V);
    root.setAttribute("data-print-zoom", snap.style.zoom);
    charts.forEach(function (c) { c.redraw(); });
  }
  function printRestore() {
    if (!wasOpen) return;
    var root = document.documentElement, snap = VIEWS.snapshot.el;
    root.classList.remove("printing");
    snap.style.width = ""; snap.style.zoom = "";
    wasOpen.forEach(function (x) { x[0].open = x[1]; });
    wasOpen = null;
    charts.forEach(function (c) { c.redraw(); });
  }
  window.addEventListener("beforeprint", printPrepare);
  window.addEventListener("afterprint", printRestore);
  window.RBOTPrint = { prepare: printPrepare, restore: printRestore };

  /* ================================================================ build */
  buildSnapshot();
  MODS.forEach(buildModule);
  buildModel();
  buildFit();
  buildEvidence();
  buildLimitations();
  main.appendChild(el("footer", { class: "foot" }, [txt("Design mockup of an RBOT Report. Caesars figures are taken from its public filings, TRACE pages and peer releases with file and line citations; every score, recommendation, valuation and thesis line is illustrative and is not a view on Caesars. Test CLO I is a synthetic portfolio.")]));
  buildNav();
  UI.init(document);

  menu.addEventListener("click", function () { sheetOpen(menu.getAttribute("aria-expanded") !== "true"); });
  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape" && menu.getAttribute("aria-expanded") === "true") { sheetOpen(false); menu.focus(); }
  });
  document.addEventListener("click", function (e) {
    if (menu.getAttribute("aria-expanded") === "true" && !e.target.closest("#pane")) sheetOpen(false);
  });
  sheet.addEventListener("click", function (e) { if (e.target.closest("a")) sheetOpen(false); });
  if ("scrollRestoration" in history) history.scrollRestoration = "manual";
  window.addEventListener("hashchange", function () { route(true); });
  route(false);

  document.documentElement.setAttribute("data-ready", "1");
  function measure() { document.documentElement.setAttribute("data-height", String(document.documentElement.scrollHeight)); }
  measure();
  if (document.fonts && document.fonts.ready) document.fonts.ready.then(function () { setTimeout(measure, 300); });
})();
