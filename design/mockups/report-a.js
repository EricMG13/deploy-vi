/* RBOT Report mockup A: IC paper. Builds the whole Report from window.RBOT_DATA with the
   shared RBOTUI / RBOTCharts layer. Every figure is a Datum printed as served; every judgement
   carries the ILLUSTRATIVE tag; module statuses, names and limitations are read at runtime.
   No innerHTML anywhere. */
(function () {
  "use strict";
  var D = window.RBOT_DATA, UI = window.RBOTUI, C = window.RBOTCharts, el = UI.el;
  var I = D.illustrative, F = D.figures, T = D.tables, K = D.charts, P = D.portfolio, M = D.meta;
  var charts = [], figs = {}, figN = 0;
  var paper = document.getElementById("paper");

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
  function kindClass(k) { return k === "total" || k === "head" ? (k === "total" ? "total" : null) : k === "sub" ? "sub" : k === "indent" ? "indent" : null; }
  function periodTable(t, filter, caption) {
    var cols = [th(t.unit || "")].concat(t.columns.map(function (c) { return th(c, null, true); }));
    var rows = t.rows.filter(filter || function () { return true; }).map(function (r) {
      var row = el("tr", { class: kindClass(r.kind) }, [rowTh(r.label)]);
      r.cells.forEach(function (d) { row.appendChild(tdD(d)); });
      return row;
    });
    return table(caption || t.title, cols, rows, "pt");
  }
  function kvTable(caption, pairs) {
    return el("table", { class: "dt dt--kv" }, [el("caption", { class: "vh", text: caption }),
      el("tbody", {}, pairs.map(function (p) { return el("tr", {}, [rowTh(p[0]), el("td", {}, p[1])]); }))]);
  }

  /* ------------------------------------------------------------ figures (numbered, captioned) */
  function draw(kind, host, spec, over) {
    figN += 1;
    var sp = Object.assign({}, spec, { number: "Figure " + figN, headingLevel: 4 }, over || {});
    var key = sp.id || ("fig-" + figN);
    sp.id = key;
    figs[key] = { n: figN, id: key };
    charts.push(C[kind](host, sp));
    return figN;
  }
  /* A figure the data cannot draw: the frame, its title and the missing input with its reason. */
  function naFigure(host, o) {
    figN += 1;
    figs[o.id] = { n: figN, id: o.id };
    var reasons = el("span", {}, []);
    o.refs.forEach(function (r) { reasons.appendChild(UI.chip(r)); });
    host.appendChild(el("figure", { class: "chart chart--na", id: o.id }, [
      el("div", { class: "chart__head" }, [el("span", { class: "chart__num", text: "Figure " + figN }),
        el("h4", { class: "chart__title", text: o.title }), el("p", { class: "chart__summary", text: o.summary })]),
      el("div", { class: "chart__plot", role: "img", "aria-label": o.title + ": not drawn, " + o.missing }, [
        el("p", { class: "chart__na" }, [el("b", { text: "n/a: not drawn" }), txt(o.missing + " "), reasons])]),
      el("p", { class: "chart__source", text: "Source: " + o.source })
    ]));
  }
  function figref(id, prefix) {
    var f = figs[id];
    if (!f) throw new Error("No figure " + id);
    return el("a", { class: "figref", href: "#" + f.id, text: (prefix || "") + "Figure " + f.n });
  }

  /* ------------------------------------------------------------ layout pieces */
  function section(id, n, title, meta) {
    var s = el("section", { class: "sec", id: id, "aria-labelledby": id + "-h" }, [
      el("div", { class: "sec-head" }, [el("span", { class: "sec-head__n", "aria-hidden": "true", text: n }),
        el("h2", { id: id + "-h" }, [el("span", { class: "vh", text: n + " " }), title]), meta ? el("span", { class: "sec-head__meta" }, meta) : null])
    ]);
    paper.appendChild(s);
    return s;
  }
  function block(parent, o) {
    var bar = el("h3", { class: "bar", id: o.id || null }, [el("span", { text: o.title }),
      o.meta ? el("span", { class: "bar__meta" }, o.meta) : null,
      o.illus ? el("span", { class: "on-navy" }, [UI.illus()]) : null,
      o.synth ? el("span", { class: "on-navy" }, [el("span", { class: "synth", text: "Synthetic" })]) : null]);
    var body = el("div", { class: o.flush ? null : "block__body" });
    var b = el("div", { class: "block " + (o.cls || "") }, [bar, body]);
    parent.appendChild(b);
    return body;
  }

  /* ================================================================ 1. CREDIT SNAPSHOT (page one) */
  function buildSnapshot() {
    var s = el("section", { class: "sec sec--snapshot", id: "snapshot", "aria-labelledby": "snapshot-h" });
    s.style.paddingTop = "0";
    paper.appendChild(s);

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
      var r = I.recommendation[st];
      call.appendChild(el("span", { class: "call__item" }, [el("span", { class: "call__k", text: st }),
        UI.scale({ kind: "rec", pos: r.pos, word: r.word, illustrative: true, label: st, size: "lg" })]));
    });
    call.appendChild(el("span", { class: "call__rule", "aria-hidden": "true" }));
    call.appendChild(el("span", { class: "call__item" }, [el("span", { class: "call__k", text: "Valuation" }),
      UI.scale({ kind: "val", pos: I.valuation.pos, illustrative: true, label: "Valuation", size: "lg" })]));
    s.appendChild(el("header", { class: "titleband" }, [
      el("div", { class: "titleband__top" }, [
        el("h1", { id: "snapshot-h", text: "Credit Snapshot: " + M.issuer }),
        el("img", { class: "brand-logo", "data-brand": "", src: "../../brand/ssim-logo-horizontal-white.png", alt: "State Street Investment Management", width: "176", height: "22" })
      ]),
      meta,
      call
    ]));

    var fp = el("div", { class: "fp" });
    s.appendChild(fp);

    /* Key findings and the main risk */
    var kf = block(fp, { title: "Key findings", id: "key-findings", cls: "span-12 p-findings", illus: true, flush: true });
    kf.appendChild(el("ol", { class: "kf" }, I.keyFindings.map(function (f) { return el("li", {}, [el("span", {}, itemNodes(f))]); })));
    var risk = I.weaknesses[0];
    kf.appendChild(el("p", { class: "kf__thesis" }, [el("b", { text: "Main risk: " + risk.label + ". " })].concat(itemNodes(risk))));

    /* Company profile: the template's fields, three label/value pairs per row */
    var prof = block(fp, { title: "Company profile", id: "company-profile", cls: "span-12 p-profile", flush: true,
      meta: [el("span", { class: "is-illus is-illus--key" }, ["dashed"]), " = illustrative"] });
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
    prof.appendChild(el("div", { class: "table-scroll" }, [el("table", { class: "dt dt--kv kv3" }, [el("caption", { class: "vh", text: "Company profile" }), pbody])]));

    /* Figures 1-4: the Model chart strip and the capital-structure chart */
    var fb = block(fp, { title: "Model chart strip and capital structure", id: "figures", cls: "span-12 p-figs", flush: true,
      meta: ["Figures 1 to 4. Select any mark for its source"] });
    var row = el("div", { class: "figrow" });
    fb.appendChild(row);
    [["lineStrip", K.leverage], ["lineStrip", K.coverage], ["lineStrip", K.liquidity], ["stackedColumns", K.maturityWall]].forEach(function (p) {
      var cell = el("div", { class: "figcell" });
      row.appendChild(cell);
      draw(p[0], cell, p[1], { height: 112, ticks: 3 });
    });

    /* Transaction summary (Primary runs only) */
    if (M.primary) {
      var tx = block(fp, { title: "Transaction summary and new debt issues", id: "transaction", cls: "span-12 p-tx", flush: true, meta: [M.primaryLabel] });
      tx.appendChild(el("div", { class: "tx__text" }, [el("p", {}, itemNodes(I.transactionSummary).concat([UI.illus()]))]));
      var g8 = gapD("G8");
      tx.appendChild(table("New debt issues", [th("Borrower"), th("Bloomberg ID (FIGI)"), th("Instrument"), th("Debt type"), th("UoP"),
        th("Tranche size", "US$ m", true), th("Guidance / IPT"), th("OID"), th("Maturity"), th("Exp. ratings"), th("CR Score"), th("Commit date")], [
        el("tr", {}, [tdD(g8, { text: true }), tdD(gapD("G28"), { text: true }),
          tdN([txt("New debt from "), UI.value(fd("merger_financing_banks_count")), txt(" banks")], "nowrap"), tdD(g8, { text: true }),
          tdN([isIllus(el("span", { class: "prov-model", text: "Acquisition" }), "Use of proceeds"), UI.chip("C12")], "nowrap"),
          tdD(g8), tdD(g8, { text: true }), tdD(g8), tdD(g8, { text: true }), tdD(g8, { text: true }), tdD(g8, { text: true }), tdD(g8, { text: true })])
      ], "wraphead"));
    }

    /* Capital structure */
    var cap = block(fp, { title: "Capital structure", id: "capital-structure", cls: "span-12 p-cap", flush: true,
      meta: ["At " + T.capitalStructure.asOf + "; multiples are cumulative, x LTM Adjusted EBITDA"] });
    cap.appendChild(capitalTable());
    cap.appendChild(el("p", { class: "chart__source", style: "padding: 0 var(--s-3) var(--s-2)" }, rich("EBITDA basis: " + T.capitalStructure.ebitda_basis + ". Financing obligations to GLPI and VICI of {C184} are shown in the balance sheet, not added to debt.")));

    /* Business description | EBITDA adjustments */
    var bd = block(fp, { title: "Business description", id: "business", cls: "span-6 p-desc", flush: true, illus: true });
    bd.appendChild(annot([el("p", {}, itemNodes(I.businessDescription))], I.businessDescription.refs));
    var adj = block(fp, { title: "EBITDA adjustments", id: "ebitda-adjustments", cls: "span-6 p-adj", flush: true, meta: [T.ebitdaAdjustments.unit + "; Reported, Structuring, SSIM"] });
    adj.appendChild(periodTable(T.ebitdaAdjustments));
    adj.appendChild(el("p", { class: "chart__source", style: "padding: 0 var(--s-3) var(--s-2)", text: T.ebitdaAdjustments.note }));

    /* Investment thesis | Catalysts */
    var th1 = block(fp, { title: "Investment thesis", id: "thesis", cls: "span-6 p-thesis", flush: true, illus: true });
    th1.appendChild(annot([el("p", {}, itemNodes(I.thesis))], I.thesis.refs));
    var cat = block(fp, { title: "Catalysts and near-term events", id: "catalysts", cls: "span-6 p-cat", flush: true, illus: true });
    cat.appendChild(el("table", { class: "dt" }, [el("caption", { class: "vh", text: "Catalysts" }), el("tbody", {}, I.catalysts.map(function (c) {
      return el("tr", {}, [el("td", {}, itemNodes(c))]);
    }))]));

    /* Credit summary | Financials, balance sheet, credit metrics */
    var cs = block(fp, { title: "Credit summary", id: "credit-summary", cls: "span-6 p-credit", flush: true, illus: true });
    function swRows(list) {
      return el("table", { class: "dt sw" }, [el("tbody", {}, list.map(function (w) {
        return el("tr", {}, [rowTh(w.label), el("td", {}, itemNodes(w))]);
      }))]);
    }
    cs.appendChild(el("div", { class: "bar bar--sub", text: "Strengths" }));
    cs.appendChild(swRows(I.strengths));
    cs.appendChild(el("div", { class: "bar bar--sub", text: "Weaknesses" }));
    cs.appendChild(swRows(I.weaknesses));
    cs.appendChild(el("div", { class: "bar bar--sub", text: "Historical performance" }));
    cs.appendChild(el("p", { style: "padding: var(--s-2) var(--s-3) 0; margin: 0" }, itemNodes(I.historicalPerformance)));
    var hp = el("div", { style: "padding: var(--s-2) var(--s-3)" });
    cs.appendChild(hp);
    draw("columns", hp, K.revenueEbitda, { height: 170 });

    var rightCol = el("div", { class: "span-6 stack p-right" });
    fp.appendChild(rightCol);
    var fin = block(rightCol, { title: "Financials", id: "financials", flush: true, meta: [T.financials.unit + "; negatives in parentheses as filed"] });
    fin.appendChild(periodTable(T.financials));
    var bs = block(rightCol, { title: "Balance sheet", id: "balance-sheet", flush: true, meta: [T.balanceSheet.unit] });
    bs.appendChild(periodTable(T.balanceSheet));
    var cm = block(rightCol, { title: "Credit metrics", id: "credit-metrics", flush: true, meta: [T.creditMetrics.unit] });
    cm.appendChild(periodTable(T.creditMetrics));
    cm.appendChild(el("p", { class: "chart__source", style: "padding: 0 var(--s-3) var(--s-2)", text: T.creditMetrics.note }));

    /* Relative value: loans and high yield */
    var lr = block(fp, { title: "Loan relative value", id: "loan-rv", cls: "span-12 p-loan", flush: true, meta: ["Index: Bloomberg US Leveraged Loan Index"] });
    lr.appendChild(loanRv());
    var hy = block(fp, { title: "High-yield relative value", id: "hy-rv", cls: "span-12 p-hy", flush: true, meta: ["Index: Bloomberg US Corporate High Yield Index; bonds: " + T.trace.title] });
    hy.appendChild(hyRv());
  }

  /* an illustrative value inside a dense block: dashed outline, named for screen readers */
  function isIllus(node, what) {
    return el("span", { class: "is-illus", title: what + ": illustrative, no RBOT run exists" }, [node, el("span", { class: "vh", text: " (illustrative)" })]);
  }
  function dirChip(word) {
    var w = String(word).toLowerCase();
    var cls = /improving|positive/.test(w) ? "up" : /deteriorating|negative/.test(w) ? "down" : "flat";
    return el("span", { class: "dir dir--" + cls, text: word });
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
      var lab = rank === "secured" ? "Senior secured debt" : rank === "unsecured" ? "Unsecured debt" : "Other debt";
      var amt = rank === "secured" ? sub.senior_secured : rank === "unsecured" ? sub.unsecured : sub.other;
      subtotal(lab, amt, rs[rs.length - 1], "total");
    });
    var last = cs.rows[cs.rows.length - 1];
    subtotal("Total debt", sub.total_debt, last, "total");
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
        return el("tr", { class: r.issuer === M.ticker ? null : null }, [rowTh(r.issuer), el("td", { class: "num", text: r.cusip }), tdD(gapD("G28"), { text: true }),
          tdD(r.moodys, { text: true }), tdD(r.sp, { text: true }), tdD(capRow ? capRow.outstanding : gapD(null, "peer issue size is not among the extracted figures")),
          tdD(r.coupon), tdD(r.maturity, { text: true }), tdD(r.next_call, { text: true }), nowrap(el("td", { text: r.seniority })), tdD(r.price), tdD(noHist), tdD(noHist),
          tdD(r.yield), tdD(g19)]);
      }), "wraphead"));
    return wrap;
  }

  /* ================================================================ 2. ANALYSIS BY MODULE */
  /* Topics carry the content; modules from RBOT_DATA decide which topics get their own section.
     A topic whose module is not in this run's module list joins its host module's detail. */
  var TOPIC_OF_ID = { "CP-0": "intake", "CP-1": "financials", "CP-1A": "business", "CP-1B": "delta", "CP-1D": "quality", "CP-2": "fundamentals",
    "CP-2A": "downside", "CP-3": "rv", "CP-4": "legal", "CP-5": "qa" };
  var HOST = { business: "financials", quality: "financials", downside: "fundamentals", fit: "rv", challenge: "downside" };
  function topicOf(m) {
    if (TOPIC_OF_ID[m.id]) return TOPIC_OF_ID[m.id];
    if (/portfolio|fit/i.test(m.name)) return "fit";
    if (/challenge|committee/i.test(m.name)) return "challenge";
    return null;
  }
  function figHost(parent) { var h = el("div", { class: "figbox" }); parent.appendChild(h); return h; }
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
  function figKv(caption, keys) {
    return el("table", { class: "dt dt--kv dt--framed" }, [el("caption", { class: "vh", text: caption }), el("tbody", {}, keys.map(function (k) {
      return el("tr", {}, [rowTh(F[k].label.charAt(0).toUpperCase() + F[k].label.slice(1)), el("td", {}, [UI.value(fd(k))])]);
    }))]);
  }
  var TOPICS = {
    intake: {
      title: "Intake and readiness",
      headline: function (m) {
        var n = docs().filter(function (d) { return !d.synthetic; }).length;
        return n + " issuer, market and peer documents are admitted; the merger's debt commitment terms [G8], a Fitch rating [G10] and rating outlooks [G11] are not in the Source Pack.";
      },
      lede: function (host, m) { host.appendChild(gapTable(m && m.refs && m.refs.length ? m.refs : ["G8", "G10", "G11"], "Gaps raised at intake")); },
      detail: function (body) {
        body.appendChild(el("h4", { text: "Documents admitted" }));
        body.appendChild(docTable());
      }
    },
    financials: {
      title: "Financial analysis and capital structure",
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
        body.appendChild(el("h4", { text: "Credit metrics and balance sheet" }));
        body.appendChild(periodTable(T.creditMetrics));
        body.appendChild(el("p", { class: "na-note", text: T.creditMetrics.note }));
        body.appendChild(periodTable(T.balanceSheet));
      }
    },
    business: {
      title: "Business and transaction",
      headline: "Fertitta Entertainment agreed on {C11} to acquire Caesars for {C210} per share in cash, a transaction valued at {C212|US$ bn} including assumed debt of {C213|US$ bn}; the new debt has no stated amount [G8].",
      lede: null,
      detail: function (body) {
        body.appendChild(figKv("Merger terms", ["issuer.merger.acquirer_brand", "issuer.merger.parent", "issuer.merger.parent_guarantor", "issuer.merger.agreement_date",
          "merger_price_per_share_pr", "merger_transaction_value", "merger_assumed_debt", "merger_premium_unaffected", "merger_premium_vwap", "issuer.merger.financing",
          "issuer.merger.financing_condition", "merger_go_shop_end", "merger_initial_end_date", "issuer.merger.caesars_advisors", "issuer.merger.fertitta_advisors"]));
        body.appendChild(el("h4", { text: "Segments, Q2 2026" }));
        body.appendChild(periodTable(T.segments));
      }
    },
    delta: {
      title: "Earnings delta",
      headline: "Q2 2026 against Q2 2025: Regional Adjusted EBITDA rose to {C96} from {C97} while Las Vegas fell to {C94} from {C95}; the cash side of the delta is available for six months only [G3].",
      lede: function (host) { draw("dumbbell", host, K.segments); },
      detail: function (body) { body.appendChild(periodTable(T.segments)); }
    },
    quality: {
      title: "Earnings quality",
      headline: "Q2 2026 Adjusted EBITDA of {K66} reconciles from a net loss of {C192}; the add-backs are transaction costs of {C204} and stock-based compensation of {C206}, and none is unrealized [G22].",
      lede: function (host) { draw("waterfall", host, K.ebitdaBridge, { height: 230 }); },
      detail: function (body) { body.appendChild(periodTable(T.ebitdaAdjustments)); body.appendChild(el("p", { class: "na-note", text: T.ebitdaAdjustments.note })); }
    },
    fundamentals: {
      title: "Fundamentals, liquidity and cash flow",
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
      title: "Downside",
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
      title: "Relative value",
      headline: "The secured 2032s last traded at {C232} to yield {C233|%} and the unsecured 2032s at {C241} to yield {C242|%}, against {C251|%} and {C260|%} for the MGM and PENN 2029s; spreads are not in the sources [G19].",
      lede: function (host) { draw("scatter", host, K.yieldCurve, { height: 230 }); },
      detail: function (body) {
        var pair = el("div", { class: "figpair" });
        body.appendChild(pair);
        draw("rangeStrip", figHost(pair), K.peerRange);
        var v = figHost(pair);
        v.appendChild(el("h4", { text: "Scores and valuation" }));
        v.appendChild(kvTable("Scores and valuation", [
          ["Credit Score", [UI.scale({ kind: "score", pos: I.creditScore.pos, word: I.creditScore.word, illustrative: true, label: "Credit Score" }), UI.illus()]],
          ["Valuation", [UI.scale({ kind: "val", pos: I.valuation.pos, illustrative: true, label: "Valuation" }), UI.illus()]],
          ["Credit Direction", [dirChip(I.creditDirection.word), UI.illus()]],
          ["Sector Outlook", [dirChip(I.sectorOutlook.word), UI.illus()]],
          ["Sponsor Quality", [el("span", { class: "prov-model", text: I.sponsorQuality.word + ". " + I.sponsorQuality.basis }), UI.illus()]]
        ].concat(M.strategies.map(function (st) {
          var r = I.recommendation[st];
          return [st, [UI.scale({ kind: "rec", pos: r.pos, word: r.word, illustrative: true, label: st }), UI.illus()]];
        }))));
        body.appendChild(el("p", { class: "na-note", text: K.peerRange.note }));
      }
    },
    legal: {
      title: "Legal and covenants",
      headline: "No maintenance covenant level is cited [G17], so headroom is not drawn against net leverage of {K56|x}; the merger agreement carries a reverse termination fee of US$ {C226} and an End Date of {C220}.",
      lede: function (host) { draw("bullet", host, K.covenant); },
      detail: function (body) {
        body.appendChild(figKv("Merger agreement protections", ["issuer.merger.financing_condition", "merger_termination_fee", "merger_termination_fee_reduced",
          "merger_reverse_termination_fee", "merger_initial_end_date", "merger_first_extended_end_date", "merger_second_extended_end_date", "merger_ticking_fee_date", "merger_ticking_fee_per_day"]));
        body.appendChild(gapTable(["G17", "G8"], "Legal documents not in the sources"));
      }
    },
    qa: {
      title: "Evidence QA",
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
          el("tr", {}, [rowTh("Q2 2026 Adjusted EBITDA bridge"), tdD(fd("recon_adj_ebitda_q2_2026")), tdD(refDatum("K66")), el("td", {}, [txt("Net loss to Adjusted EBITDA reconciles; "), figref("fig-ebitda-bridge", "see ")])]),
          el("tr", {}, [rowTh("H1 2026 cash bridge"), tdD(refDatum("C104")), tdD(refDatum("K67")), el("td", {}, [txt("Residual unexplained by the extracted lines; "), figref("fig-cash-bridge", "see ")])])
        ]));
      }
    },
    fit: {
      title: "Portfolio Fit",
      headline: function () { return P.fit.summary; },
      synthetic: true,
      lede: function (host) { draw("rangeStrip", host, K.cloSectors); },
      detail: function (body) {
        body.appendChild(el("p", {}, [txt("The checks, per-instrument fit and the Test CLO I constraint schedule are in "), el("a", { href: "#portfolio-fit", text: "section 4, Portfolio Fit" }), txt(".")]));
      }
    },
    challenge: {
      title: "Committee challenge",
      headline: "Would the secured 2032s hold value if the merger adds debt of unknown size [G8], and is the fall in Las Vegas Adjusted EBITDA to {C94} from {C95} cyclical or structural?",
      lede: function (host) {
        host.appendChild(table("Challenges", [th("Challenge"), th("Rests on")], I.weaknesses.map(function (w) {
          return el("tr", {}, [rowTh(w.label), el("td", {}, itemNodes(w).concat([UI.illus()]))]);
        })));
      },
      detail: function (body) { body.appendChild(el("p", { class: "na-note", text: "Responses to each challenge would come from the run; none exists for this mockup." })); }
    }
  };
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
  function headlineNodes(t, m) {
    var str = typeof t.headline === "function" ? t.headline(m) : t.headline;
    var nodes = authored(rich(str));
    if (t.synthetic) nodes.push(el("span", { class: "synth", text: "Synthetic" }));
    return { nodes: nodes, refs: refsIn(str) };
  }

  function buildAnalysis(rail) {
    var mods = D.modules;
    var tally = {};
    mods.forEach(function (m) { tally[m.status] = (tally[m.status] || 0) + 1; });
    var s = section("analysis", "2", "Analysis by module", [mods.length + " modules: " + Object.keys(tally).map(function (k) { return tally[k] + " " + k; }).join(", ")]);
    s.appendChild(el("p", { class: "sec-lede" }, ["Each module opens on its headline finding and its figure. The status and its reason come from the run record; ",
      el("span", { class: "prov-model", text: "headlines are model-authored" }), el("span", { class: "tag-model", text: "Model" }), " and illustrative, because no RBOT run exists."]));
    var owned = {};
    mods.forEach(function (m) { var t = topicOf(m); if (t) owned[t] = m; });
    mods.forEach(function (m, i) {
      var t = topicOf(m), n = "2." + (i + 1), id = slug(m.id);
      rail.push({ n: n, id: id, t: m.id + " " + m.name, status: m.status });
      var box = el("article", { class: "mod", id: id, "aria-labelledby": id + "-h" });
      s.appendChild(box);
      box.appendChild(el("h3", { class: "bar", id: id + "-h" }, [el("span", {}, [el("span", { class: "bar__n", text: n }), txt(m.id + "  " + m.name)]),
        el("span", { class: "on-navy" }, [UI.status(m.status)])]));
      var lede = el("div", { class: "mod__lede" });
      box.appendChild(lede);
      var leftCol = el("div"), rightCol = el("div");
      lede.appendChild(leftCol); lede.appendChild(rightCol);
      var topic = t ? TOPICS[t] : null;
      if (topic) {
        var hl = headlineNodes(topic, m);
        leftCol.appendChild(el("p", { class: "lede-line" }, hl.nodes));
      }
      var st = el("p", { class: "mod__status" }, [el("b", { text: m.status + ". " }), txt(m.reason + " ")]);
      (m.refs || []).forEach(function (r) { st.appendChild(UI.chip(r)); });
      leftCol.appendChild(st);
      if (topic && topic.lede) topic.lede(rightCol, m);
      else rightCol.appendChild(el("p", { class: "na-note", text: "No figure for this module." }));
      var det = el("details", { class: "xp xp--light", id: id + "-detail" }, [el("summary", { text: "Detailed analysis, tables and sources" })]);
      var body = el("div", { class: "xp__body" });
      det.appendChild(body);
      box.appendChild(det);
      if (topic && hl.refs.length) body.appendChild(el("div", { class: "src-notes" }, [el("h4", { text: "Sources for the headline" }), notes(hl.refs)]));
      if (topic && topic.detail) topic.detail(body, m);
      /* topics with no module of their own join this one */
      Object.keys(HOST).forEach(function (sub) {
        if (HOST[sub] !== t || owned[sub]) return;
        var tp = TOPICS[sub];
        var wrap = el("div", { class: "sub", id: id + "-" + sub });
        body.appendChild(wrap);
        wrap.appendChild(el("h4", { text: tp.title }));
        var h2 = headlineNodes(tp);
        wrap.appendChild(el("p", { class: "lede-line" }, h2.nodes));
        if (tp.lede) tp.lede(figHost(wrap));
        if (tp.detail) tp.detail(wrap);
      });
      if (!body.childNodes.length) body.appendChild(el("p", { class: "na-note", text: "No further detail for this module." }));
    });
  }

  /* ================================================================ 3. MODEL */
  function buildModel(rail) {
    var s = section("model", "3", "Model", ["Values-only twin of model.xlsx. Select any cell for its passport: source, locator, excerpt or formula"]);
    var fin = T.financials;
    var earningsRows = function (r, i) { return i <= 5; };
    var cashRows = function (r, i) { return i >= 6; };
    var bands = [
      { id: "model-earnings", t: "Earnings", lede: "LTM net revenues {K1} and Adjusted EBITDA {K2}, a margin of {K47|%}; FY2023 Adjusted EBITDA was {C74}.",
        fig: "fig-rev-ebitda", body: function (b) { b.appendChild(periodTable(fin, earningsRows, "Earnings")); } },
      { id: "model-ebitda-bridge", t: "Adjusted EBITDA bridge", lede: "Q2 2026 Reported EBITDA {K65} plus transaction costs {C204} and stock-based compensation {C206} gives Structuring EBITDA {K66}; SSIM equals Structuring [G22].",
        fig: "fig-ebitda-bridge", body: function (b) { b.appendChild(periodTable(T.ebitdaAdjustments)); b.appendChild(el("p", { class: "na-note", text: T.ebitdaAdjustments.note })); } },
      { id: "model-cash-flow", t: "Cash flow waterfall", lede: "LTM cash from operations {K4} less capex {K3} leaves free cash flow of {K50}; lease cash interest of {K9} runs through rent.",
        fig: "fig-cash-bridge", body: function (b) { b.appendChild(periodTable(fin, cashRows, "Cash flow")); } },
      { id: "model-debt-stack", t: "Debt stack by rank", lede: "Senior secured {K57}, unsecured {K58} and other {K59}: total debt {C114} at face; financing obligations of {C184} are shown apart from debt.",
        fig: "fig-debt-stack", body: function (b) { b.appendChild(debtStack()); } },
      { id: "model-credit-metrics", t: "Credit metrics", lede: "Total leverage {K55|x}, net {K56|x} and senior {K61|x}; interest cover {K51|x}, or {K52|x} on debt cash interest alone.",
        fig: "fig-leverage", body: function (b) { b.appendChild(periodTable(T.creditMetrics)); b.appendChild(periodTable(T.balanceSheet)); } }
    ];
    bands.forEach(function (bd, i) {
      var n = "3." + (i + 1);
      rail.push({ n: n, id: bd.id, t: bd.t });
      var box = el("div", { class: "mod band", id: bd.id });
      s.appendChild(box);
      box.appendChild(el("h3", { class: "bar" }, [el("span", {}, [el("span", { class: "bar__n", text: n }), txt(bd.t)])]));
      box.appendChild(el("p", { class: "xp__lede band__lede" }, [el("span", { class: "band__text" }, rich(bd.lede)), figref(bd.fig, "Drawn in ")]));
      var det = el("details", { class: "xp xp--light", id: bd.id + "-rows" }, [el("summary", { text: "Band rows" })]);
      var body = el("div", { class: "xp__body" });
      det.appendChild(body);
      box.appendChild(det);
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
    var s = section("portfolio-fit", "4", "Portfolio Fit: " + P.name, [el("span", { class: "synth", text: "Synthetic" }), " ", UI.illus(), " Portfolio as of " + P.asOf]);
    var grid = el("div", { class: "pf-summary" });
    s.appendChild(grid);
    var left = el("div"), right = el("div");
    grid.appendChild(left); grid.appendChild(right);
    left.appendChild(el("div", { class: "pf-verdict" }, [el("h3", { text: "Portfolio Fit" }), UI.status(fit.overall.v), UI.illus()]));
    left.appendChild(el("p", {}, [el("span", { class: "prov-model", text: fit.summary }), el("span", { class: "tag-model", text: "Model" })]));
    left.appendChild(table("Fit checks", [th("Constraint"), th("Limit"), th("Current", null, true), th("Headroom", null, true), th("Result")], fit.checks.map(function (c) {
      return el("tr", {}, [el("th", { scope: "row" }, [txt(c.constraint), UI.chip(c.ref)]), nowrap(el("td", { text: c.limit })), el("td", { class: "num", text: c.current }),
        el("td", { class: "num", text: c.headroom }), el("td", {}, [UI.status(c.result), c.note ? el("div", { class: "gap__reason", text: c.note }) : null])]);
    })));
    left.appendChild(el("h4", { style: "margin-top: var(--s-4)", text: "Fit by instrument" }));
    left.appendChild(table("Fit by instrument", [th("Instrument"), th("Fit"), th("Note")], fit.byInstrument.map(function (b) {
      return el("tr", {}, [rowTh(b.instrument), el("td", {}, [UI.status(b.fit)]), el("td", { text: b.note || "" })]);
    })));
    draw("bullet", right, K.cloLimits);
    var det = el("details", { class: "xp", id: "portfolio-fit-detail" }, [el("summary", { text: "Test CLO I: constraints, summary, mandate and sectors" })]);
    var body = el("div", { class: "xp__body" });
    det.appendChild(body);
    s.appendChild(el("div", { style: "margin-top: var(--s-4)" }, [det]));
    body.appendChild(el("h4", { text: "Constraint schedule" }));
    body.appendChild(table("Constraints", [th("ID"), th("Category"), th("Parameter"), th("Limit"), th("Type"), th("Current", null, true), th("Headroom", null, true), th("Status"), th("Source")],
      P.constraints.map(function (c) {
        return el("tr", {}, [el("th", { scope: "row" }, [txt(c.id), UI.chip(c.ref)]), el("td", { text: c.category }), el("td", { text: c.parameter }), el("td", { text: c.limit }),
          el("td", { text: c.breachType }), el("td", { class: "num", text: c.current }), el("td", { class: "num", text: c.headroom }), el("td", {}, [UI.status(c.status)]), el("td", { text: c.sourceDocument })]);
      })));
    var pair = el("div", { class: "figpair", style: "margin-top: var(--s-4)" });
    body.appendChild(pair);
    function kvd(obj, cap) {
      return el("table", { class: "dt dt--kv dt--framed" }, [el("caption", { text: cap }), el("tbody", {}, Object.keys(obj).map(function (k) {
        var c = el("td"); UI.cell(c, obj[k]);
        return el("tr", {}, [rowTh(k), c]);
      }))]);
    }
    pair.appendChild(kvd(P.summary, "Portfolio summary"));
    pair.appendChild(kvd(P.mandate, "Mandate"));
    body.appendChild(el("h4", { style: "margin-top: var(--s-4)", text: "Sector weights" }));
    body.appendChild(table("Sectors", [th("Sector"), th("% NAV", null, true), th("Issuers", null, true), th("Limit"), th("Headroom", null, true), th("Status")],
      P.sectors.map(function (x) {
        return el("tr", {}, [rowTh(x.sector), el("td", { class: "num", text: x.pct }), el("td", { class: "num", text: x.issuers }), el("td", { text: x.limit }),
          el("td", { class: "num", text: x.headroom }), el("td", {}, [UI.status(x.status)])]);
      })));
  }

  /* ================================================================ 5. EVIDENCE */
  function buildEvidence() {
    var c = D.counts;
    var s = section("evidence", "5", "Evidence", [c.cited + " cited, " + c.calculated + " calculated, " + c.gaps + " gaps, " + c.synthetic_sources + " synthetic"]);
    s.appendChild(el("p", { class: "sec-lede", text: "Every citation with its verbatim excerpt, every calculation with its formula and inputs. The table below counts citations by document; open the registers for every record." }));
    s.appendChild(docTable());
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
    ].forEach(function (x, i) {
      var det = el("details", { class: "xp", id: x[0], style: i === 0 ? "margin-top: var(--s-4)" : null }, [el("summary", { text: x[1] })]);
      var body = el("div", { class: "xp__body" }, [x[2]()]);
      det.appendChild(body);
      s.appendChild(det);
    });
  }
  function tall(node) { node.classList.add("tall-scroll"); return node; }

  /* ================================================================ 6. LIMITATIONS */
  function buildLimitations() {
    var L = D.limitations;
    var byScope = {};
    L.forEach(function (l) { byScope[l.scope] = (byScope[l.scope] || 0) + 1; });
    var s = section("limitations", "6", "Limitations", [L.length + " known at Approval"]);
    s.appendChild(el("p", { class: "sec-lede", text: "Stated before the run and carried into the Report. " + Object.keys(byScope).map(function (k) { return k + ": " + byScope[k]; }).join(" · ") + "." }));
    var model = L.filter(function (l) { return /^Model limitation/.test(l.scope); });
    function limRows(list) {
      return list.map(function (l) {
        return el("tr", {}, [el("th", { scope: "row" }, [UI.chip(l.ref)]), el("td", { text: l.field }), el("td", { text: l.text }), el("td", { text: l.scope }), el("td", { text: l.origin })]);
      });
    }
    var cols = function () { return [th("Gap"), th("Field"), th("Limitation"), th("Scope"), th("Origin")]; };
    var sub1 = el("div", { class: "sub", id: "limitations-known" }, [el("div", { class: "sub-head" }, [el("span", { class: "sub-head__n", text: "6.1" }), el("h3", { text: "Known at Approval" })])]);
    s.appendChild(sub1);
    if (model.length) {
      sub1.appendChild(el("p", { text: "These limit the Model itself:" }));
      sub1.appendChild(table("Model limitations", cols(), limRows(model)));
    }
    var det = el("details", { class: "xp", id: "limitations-all", style: "margin-top: var(--s-3)" }, [el("summary", { text: "All " + L.length + " limitations known at Approval" })]);
    det.appendChild(el("div", { class: "xp__body" }, [table("Limitations known at Approval", cols(), limRows(L))]));
    sub1.appendChild(det);
    var sub2 = el("div", { class: "sub", id: "limitations-unforeseen" }, [el("div", { class: "sub-head" }, [el("span", { class: "sub-head__n", text: "6.2" }), el("h3", { text: "Unforeseen" })])]);
    s.appendChild(sub2);
    var U = D.unforeseen || [];
    if (U.length) sub2.appendChild(table("Unforeseen limitations", cols(), limRows(U)));
    else sub2.appendChild(el("p", { text: "None recorded. No RBOT run exists, so nothing arose after Approval." }));
    paper.appendChild(el("footer", { class: "foot" }, [txt("Design mockup of an RBOT Report. Caesars figures are taken from its public filings, TRACE pages and peer releases with file and line citations; every score, recommendation, valuation and thesis line is illustrative and is not a view on Caesars. Test CLO I is a synthetic portfolio.")]));
  }

  /* ================================================================ contents rail */
  function buildRail(entries) {
    var nav = document.getElementById("toc");
    var list = el("ol", { class: "toc" });
    entries.forEach(function (e) {
      var li = el("li", {}, [el("a", { href: "#" + e.id, "data-target": e.id }, [el("span", { class: "toc__n", text: e.n }), el("span", { class: "toc__t", text: e.t })])]);
      if (e.subs && e.subs.length) {
        li.appendChild(el("ol", {}, e.subs.map(function (x) {
          return el("li", {}, [el("a", { href: "#" + x.id, "data-target": x.id }, [el("span", { class: "toc__n", text: x.n }), el("span", { class: "toc__t", text: x.t }),
            x.status ? UI.status(x.status) : null])]);
        })));
      }
      list.appendChild(li);
    });
    nav.appendChild(list);
    var links = Array.prototype.slice.call(nav.querySelectorAll("a[data-target]"));
    var where = document.getElementById("rail-where");
    function current() {
      var best = null;
      links.forEach(function (a) {
        var t = document.getElementById(a.getAttribute("data-target"));
        if (t && t.getBoundingClientRect().top <= 140) best = a;
      });
      if (!best) best = links[0];
      links.forEach(function (a) { if (a === best) a.setAttribute("aria-current", "location"); else a.removeAttribute("aria-current"); a.classList.remove("is-in"); });
      var parentLi = best.closest("ol ol") ? best.closest("ol ol").parentElement : null;
      if (parentLi) parentLi.firstElementChild.classList.add("is-in");
      if (where) where.textContent = best.querySelector(".toc__n").textContent + " " + best.querySelector(".toc__t").textContent;
    }
    var raf = 0;
    window.addEventListener("scroll", function () { cancelAnimationFrame(raf); raf = requestAnimationFrame(current); }, { passive: true });
    current();
    /* phone: the rail collapses to a bar with a Contents button */
    var toggle = document.getElementById("rail-toggle"), panel = document.getElementById("rail-panel");
    toggle.addEventListener("click", function () {
      var open = toggle.getAttribute("aria-expanded") !== "true";
      toggle.setAttribute("aria-expanded", String(open));
      panel.hidden = !open;
    });
    nav.addEventListener("click", function (e) {
      if (e.target.closest("a") && toggle.offsetParent !== null) { toggle.setAttribute("aria-expanded", "false"); panel.hidden = true; }
    });
    var all = document.getElementById("open-all");
    all.addEventListener("click", function () {
      var open = all.getAttribute("aria-pressed") !== "true";
      all.setAttribute("aria-pressed", String(open));
      all.textContent = open ? "Close all sections" : "Open all sections";
      document.querySelectorAll("details.xp").forEach(function (d) { d.open = open; });
    });
  }

  /* deep links: open every closed section around the target, then bring it into view */
  function reveal(id, smooth) {
    if (!id) return;
    var t = document.getElementById(decodeURIComponent(id));
    if (!t) return;
    for (var p = t; p; p = p.parentElement) if (p.tagName === "DETAILS") p.open = true;
    if (t.tagName === "DETAILS") t.open = true;
    t.scrollIntoView({ block: "start", behavior: smooth ? "smooth" : "auto" });
  }

  /* print: page one (the Credit Snapshot) is re-flowed into a paper column and a wide column and
     scaled to fit one landscape page; every section after it prints open. */
  var PAGE_W = 985, PAGE_H = 712;   /* CSS px inside @page margins; fits both US Letter and A4 landscape */
  var wasOpen = [], fpOrder = null, printRight = null;
  function q(sel) { return document.querySelector(sel); }
  function printPrepare() {
    if (fpOrder) return;
    var root = document.documentElement, snap = document.getElementById("snapshot"), fp = q("#snapshot .fp");
    wasOpen = [];
    document.querySelectorAll("details").forEach(function (d) { wasOpen.push([d, d.open]); d.open = true; });
    UI.close(false);
    fpOrder = Array.prototype.slice.call(fp.children);
    var colA = el("div", { class: "pcol" }), colR = el("div", { class: "pcol" }), sub = el("div", { class: "psub" });
    [".p-findings", ".p-profile", ".p-desc", ".p-thesis", ".p-cat", ".p-adj", ".p-credit"].forEach(function (c) { var n = q("#snapshot " + c); if (n) colA.appendChild(n); });
    [".p-figs", ".p-tx", ".p-cap"].forEach(function (c) { var n = q("#snapshot " + c); if (n) colR.appendChild(n); });
    var right = q("#snapshot .p-right"), rightKids = Array.prototype.slice.call(right.children), side = el("div", { class: "stack" });
    sub.appendChild(rightKids[0]);
    rightKids.slice(1).forEach(function (n) { side.appendChild(n); });
    sub.appendChild(side);
    printRight = { box: right, kids: rightKids };
    colR.appendChild(sub);
    [".p-loan", ".p-hy"].forEach(function (c) { var n = q("#snapshot " + c); if (n) colR.appendChild(n); });
    fp.appendChild(colA); fp.appendChild(colR);
    root.classList.add("printing");
    /* try a few virtual widths; at each, settle the zoom on the rendered size (text reflows under zoom) */
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
    [2000, 2400, 2800, 3200].forEach(function (V) { var z = settle(V); if (!best || z > best.z) best = { V: V, z: z }; });
    settle(best.V);
    root.setAttribute("data-print-zoom", snap.style.zoom);
  }
  function printRestore() {
    if (!fpOrder) return;
    var root = document.documentElement, snap = document.getElementById("snapshot"), fp = q("#snapshot .fp");
    printRight.kids.forEach(function (n) { printRight.box.appendChild(n); });
    fpOrder.forEach(function (n) { fp.appendChild(n); });
    Array.prototype.slice.call(fp.querySelectorAll(".pcol")).forEach(function (n) { n.parentNode.removeChild(n); });
    fpOrder = null;
    root.classList.remove("printing");
    snap.style.width = ""; snap.style.zoom = "";
    wasOpen.forEach(function (x) { x[0].open = x[1]; });
    charts.forEach(function (c) { c.redraw(); });
  }
  window.addEventListener("beforeprint", printPrepare);
  window.addEventListener("afterprint", printRestore);
  window.RBOTPrint = { prepare: printPrepare, restore: printRestore };

  /* ================================================================ build */
  var rail = [
    { n: "1", id: "snapshot", t: "Credit Snapshot", subs: [
      { n: "1.1", id: "key-findings", t: "Key findings" },
      { n: "1.2", id: "company-profile", t: "Company profile" },
      { n: "1.3", id: "figures", t: "Charts" },
      { n: "1.4", id: "transaction", t: "Transaction summary" },
      { n: "1.5", id: "capital-structure", t: "Capital structure" },
      { n: "1.6", id: "business", t: "Business and thesis" },
      { n: "1.7", id: "credit-summary", t: "Credit summary and financials" },
      { n: "1.8", id: "loan-rv", t: "Relative value" }] },
    { n: "2", id: "analysis", t: "Analysis by module", subs: [] },
    { n: "3", id: "model", t: "Model", subs: [] },
    { n: "4", id: "portfolio-fit", t: "Portfolio Fit" },
    { n: "5", id: "evidence", t: "Evidence" },
    { n: "6", id: "limitations", t: "Limitations" }
  ];
  if (!M.primary) rail[0].subs = rail[0].subs.filter(function (x) { return x.id !== "transaction"; });
  document.getElementById("rail-issuer").textContent = M.issuer.replace(/, Inc\.$/, "") + " (" + M.ticker + ")";
  document.getElementById("rail-meta").textContent = M.pathway + " · " + M.reportingPeriod;

  buildSnapshot();
  buildAnalysis(rail[1].subs);
  buildModel(rail[2].subs);
  buildFit();
  buildEvidence();
  buildLimitations();
  buildRail(rail);
  UI.init(document);

  if (location.hash) reveal(location.hash.slice(1), false);
  window.addEventListener("hashchange", function () { reveal(location.hash.slice(1), true); });

  /* ?demo=expanded: two sections open and one citation popover, for the review screenshot */
  if (/[?&]demo=expanded\b/.test(location.search)) {
    var a = document.getElementById("model-earnings-rows"), b = document.getElementById("model-ebitda-bridge-rows");
    a.open = true; b.open = true;
    requestAnimationFrame(function () {
      document.getElementById("model-earnings").scrollIntoView({ block: "start" });
      var cellBtn = b.querySelector("td.prov--cited .cellref");
      UI.open(cellBtn.getAttribute("data-ref"), cellBtn);
      document.documentElement.setAttribute("data-demo", "1");
    });
  }
  document.documentElement.setAttribute("data-ready", "1");
  function measure() { document.documentElement.setAttribute("data-height", String(document.documentElement.scrollHeight)); }
  measure();
  if (document.fonts && document.fonts.ready) document.fonts.ready.then(function () { setTimeout(measure, 300); });
})();
