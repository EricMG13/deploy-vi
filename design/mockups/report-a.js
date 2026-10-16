/* RBOT Report mockup A: IC paper as an app shell.
   A persistent left navigation pane and a set of hash-routed views: the Credit Snapshot (a summary
   screen), one view per module with its full analysis, then Model, Portfolio Fit, Evidence and
   Limitations. Built from window.RBOT_DATA with the shared RBOTUI / RBOTCharts layer. Every figure is a
   Datum shown by unit (the passport keeps the string exactly as served); judgements carry the
   ILLUSTRATIVE tag; model-written blocks are marked once; module statuses, names and limitations are
   read at runtime. No innerHTML anywhere. */
(function () {
  "use strict";
  var D = window.RBOT_DATA, UI = window.RBOTUI, C = window.RBOTCharts, el = UI.el;
  var I = D.illustrative, F = D.figures, T = D.tables, K = D.charts, P = D.portfolio, M = D.meta, OM = T.operatingModel;
  var charts = [], FIGS = {}, figCount = {}, curView = "snapshot", curPre = "S", subLevel = 3, gapHref = null;
  var main = document.getElementById("main");
  var VIEWS = {}, ORDER = [], PRE = {};

  /* ------------------------------------------------------------ display formatting (the passport keeps the served string) */
  var MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"];
  var MON3 = MONTHS.map(function (m) { return m.slice(0, 3); });
  function monIdx(name) { return MON3.map(function (x) { return x.toLowerCase(); }).indexOf(String(name).toLowerCase().slice(0, 3)); }
  function parseDate(s) {
    var m;
    if ((m = /^(\d{4})-(\d{2})-(\d{2})$/.exec(s))) return { d: +m[3], m: +m[2] - 1, y: +m[1] };
    if ((m = /^(\d{1,2})\/(\d{1,2})\/(\d{4})$/.exec(s))) return { d: +m[2], m: +m[1] - 1, y: +m[3] };
    if ((m = /^([A-Za-z]+) (\d{1,2}), (\d{4})$/.exec(s)) && monIdx(m[1]) >= 0) return { d: +m[2], m: monIdx(m[1]), y: +m[3] };
    if ((m = /^(\d{1,2})[- ]([A-Za-z]{3,9})[- ](\d{4})$/.exec(s)) && monIdx(m[2]) >= 0) return { d: +m[1], m: monIdx(m[2]), y: +m[3] };
    return null;
  }
  function fmtDate(p, style) { return p.d + " " + (style === "prose" ? MONTHS[p.m] : MON3[p.m]) + " " + p.y; }
  /* dates inside running text: "30 June 2026" in prose, "15 Feb 2032" inside tables */
  var DATE_RES = [
    [/\b(January|February|March|April|May|June|July|August|September|October|November|December) (\d{1,2}), (\d{4})/g, function (m, mo, d, y) { return { d: +d, m: monIdx(mo), y: +y }; }],
    [/\b(\d{4})-(\d{2})-(\d{2})\b/g, function (m, y, mo, d) { return { d: +d, m: +mo - 1, y: +y }; }],
    [/\b(\d{1,2})-(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)-(\d{4})\b/g, function (m, d, mo, y) { return { d: +d, m: monIdx(mo), y: +y }; }],
    [/\b(\d{1,2}) (Jan|Feb|Mar|Apr|Jun|Jul|Aug|Sep|Oct|Nov|Dec) (\d{4})\b/g, function (m, d, mo, y) { return { d: +d, m: monIdx(mo), y: +y }; }]
  ];
  function textDates(s, style) {
    DATE_RES.forEach(function (r) { s = s.replace(r[0], function () { return fmtDate(r[1].apply(null, arguments), style); }); });
    return s;
  }
  function numParts(s) {
    var t = String(s).trim(), neg = false;
    if (/^\(.*\)$/.test(t)) { neg = true; t = t.slice(1, -1); }
    if (/^[-−]/.test(t)) { neg = !neg; t = t.slice(1); }
    t = t.replace(/,/g, "");
    if (!/^\d*\.?\d+$/.test(t)) return null;
    return { neg: neg, n: parseFloat(t), dp: (t.split(".")[1] || "").length, raw: t };
  }
  function grouped(n, dp) { return n.toLocaleString("en-US", { minimumFractionDigits: dp, maximumFractionDigits: dp }); }
  /* yields and coupons: 3 decimals at most, trailing zeros trimmed to 2 (4.125, 6.50, 8.064) */
  function rateText(p) { var t = p.n.toFixed(3); return /0$/.test(t) ? t.slice(0, -1) : t; }
  function trimZeros(t) { return t.indexOf(".") < 0 ? t : t.replace(/0+$/, "").replace(/\.$/, ""); }
  var UNIT_OF = { "USD millions": "US$ m", "USD billions": "US$ bn", "USD thousands": "US$ k", "USD": "US$", "USD per share": "US$/sh",
    "USD per share per day": "US$/sh/day", "%": "%", "x": "x", "price": "price" };
  function textMoney(s) {
    return s.replace(/\$(\d[\d.,]*) (billion|million)/g, function (m, n, w) { return "US$" + n + (w === "billion" ? "bn" : "m"); });
  }
  function displayFormat(d, unit, ctx, kind) {
    var s = String(d.v), dt = parseDate(s);
    if (dt) return fmtDate(dt, ctx === "prose" ? "prose" : "table");
    var p = numParts(s);
    if (!p) return d.unit === "text" || !d.unit ? textMoney(s) : null;
    var u = unit || UNIT_OF[d.unit] || null;
    function wrap(t) { return p.neg ? "(" + t + ")" : t; }
    if (u === "bare") return p.dp >= 4 ? wrap(rateText(p)) : s;
    switch (u) {
      case "US$ m": return wrap("US$" + grouped(p.n, p.dp) + "m");
      case "US$ bn": return wrap("US$" + grouped(p.n, p.dp) + "bn");
      case "US$ k": return wrap("US$" + grouped(p.n, p.dp) + "k");
      case "US$": return wrap(p.n >= 1e6 && p.n % 1e5 === 0 ? "US$" + trimZeros(String(p.n / 1e6)) + "m" : "US$" + grouped(p.n, p.dp));
      case "US$/sh": return "US$" + p.raw + " per share";
      case "US$/sh/day": return "US$" + trimZeros(p.raw) + " per share per day";
      case "%": return p.dp >= 4 ? wrap(rateText(p) + "%") : (p.neg ? "-" : "") + grouped(p.n, p.dp) + "%";
      case "x": return wrap(p.n.toFixed(2) + "x");
      case "price": return p.n.toFixed(2);
    }
    if (kind === "rate" || (!u && p.dp >= 4)) return wrap(rateText(p));
    if (kind === "price") return wrap(p.n.toFixed(2));
    return null;
  }
  UI.setFormat(displayFormat);
  UI.setTextHook(function (s) { return textDates(s, "table"); });
  /* every date in the built page reads the same way; the evidence register and the passport keep the served strings */
  function tidyDates(root) {
    var w = document.createTreeWalker(root, NodeFilter.SHOW_TEXT, null), n, todo = [];
    while ((n = w.nextNode())) {
      var pe = n.parentElement;
      if (!pe || pe.closest(".evid, .pop, script, style, code")) continue;
      todo.push(n);
    }
    todo.forEach(function (node) {
      var t = node.nodeValue, r = textDates(t, node.parentElement.closest("table, .chart, .kv__when") ? "table" : "prose");
      if (r !== t) node.nodeValue = r;
    });
    /* names and tooltips read the same dates as the page */
    Array.prototype.forEach.call(root.querySelectorAll("[aria-label], [title]"), function (n) {
      if (n.closest(".evid, .pop")) return;
      ["aria-label", "title"].forEach(function (a) {
        var t = n.getAttribute(a);
        if (t) { var r = textDates(t, "table"); if (r !== t) n.setAttribute(a, r); }
      });
    });
  }

  /* ------------------------------------------------------------ small helpers */
  function txt(s) { return document.createTextNode(s); }
  function slug(s) { return String(s).toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, ""); }
  /* gap fields are the extraction's keys; the reader gets plain names */
  var GAP_LABEL = {
    "cash_interest_paid_q2_2026 / q2_2025": "Cash interest paid, Q2 2026 and Q2 2025", "income_taxes_paid_q2_2026 / q2_2025": "Income taxes paid, Q2 2026 and Q2 2025",
    "cfo_q2_2026 / q2_2025": "Cash from operations, Q2 2026 and Q2 2025", "capex_q2 purchase of property and equipment (cash flow basis)": "Q2 capex on a cash flow basis",
    "operating_lease_liability_2026_06_30": "Operating lease liability at 30 June 2026", "cva_rcf_drawn / availability as separate figure": "CVA revolver drawn and availability, separately",
    "merger_expected_closing": "Expected closing of the merger", "merger_committed_debt_financing_amount": "Committed merger debt financing amount",
    "merger_financing_bank_names": "Names of the merger financing banks", "rating_fitch": "Fitch rating", "rating_outlooks_moodys_sp": "Rating outlooks (Moody's, S&P)",
    "trace_security_description": "TRACE security description", "czr_financial_guidance_revenue_ebitda": "Company revenue and EBITDA guidance",
    "mgm_consolidated_adj_ebitdar / penn_consolidated_adj_ebitdar": "MGM and PENN consolidated Adjusted EBITDAR", "total_debt_cash_fy2023_fy2024": "Debt and cash at FY2023 and FY2024 year-end",
    "liquidity_fy2023_fy2025": "Total liquidity, FY2023 to FY2025", "covenant_levels": "Covenant levels", "loan_margins_prices": "Loan margins and prices",
    "spread_to_treasury": "Spread to Treasury", "reported_ebitda_ltm": "LTM Reported EBITDA", "pf_ltm": "PF-LTM column", "unrealized_addbacks": "Unrealized add-backs",
    "gross_profit": "Gross profit", "morningstar_issuer_id": "Morningstar Issuer ID", "issuer_ratings": "Issuer ratings", "cash_flow_detail_h1_2026": "H1 2026 investing and financing cash flows",
    "equity_market_value": "Equity market value", "figi": "Bloomberg ID (FIGI)"
  };
  function human(field) {
    if (GAP_LABEL[field]) return GAP_LABEL[field];
    var t = String(field).replace(/_/g, " ");
    return t.charAt(0).toUpperCase() + t.slice(1);
  }
  function cap(s) { s = String(s || ""); return s.charAt(0).toUpperCase() + s.slice(1); }
  UI.setFieldLabel(function (f) { return human(f); });
  function originText(o) { return /czr\.json/i.test(o) ? "Source extraction" : /build-data/i.test(o) ? "Model build" : o; }
  function gapD(ref, reason) {
    return { v: null, prov: "gap", ref: ref || undefined, reason: reason || (ref && D.gaps[ref] ? D.gaps[ref].reason : "not in the sources") };
  }
  var REF_UNIT = {}, FIG_BY_REF = {};
  Object.keys(F).forEach(function (k) {
    var f = F[k];
    if (f.ref && !(f.ref in FIG_BY_REF)) { FIG_BY_REF[f.ref] = f.v; REF_UNIT[f.ref] = f.unit; }
  });
  function fd(key) {
    var f = F[key];
    if (!f) throw new Error("No figure " + key + " in RBOT_DATA.figures");
    return { v: f.v, prov: f.prov, ref: f.ref, reason: f.reason, unit: f.unit };
  }
  /* a figure's presented value (filings' parentheses) wins over the raw record value */
  function refDatum(ref) {
    var c = D.citations[ref];
    if (c) return { v: ref in FIG_BY_REF ? FIG_BY_REF[ref] : c.value, prov: c.synthetic ? "synthetic" : "cited", ref: ref, unit: REF_UNIT[ref] || c.unit };
    var k = D.calcs[ref];
    if (k) return { v: ref in FIG_BY_REF ? FIG_BY_REF[ref] : k.value, prov: "calculated", ref: ref, unit: REF_UNIT[ref] };
    if (D.gaps[ref]) return gapD(ref);
    throw new Error("Unknown reference " + ref);
  }
  /* rich("text {K55|x} more [G8]"): {REF} prints the record's value, the figure itself the button; [REF] a chip alone */
  var TOKEN = /\{([CKGS]\d+)(?:\|([^}]*))?\}|\[([CKGS]\d+)\]/g;
  function rich(str) {
    /* "3,592 [K2]": a figure followed by its own reference reads as the figure alone, the figure being the button */
    str = str.replace(/(\d[\d,]*(?:\.\d+)?)\s*\[([CKS]\d+)\]/g, function (all, n, ref) {
      var d = D.citations[ref] || D.calcs[ref];
      return d && String(refDatum(ref).v) === n ? "{" + ref + "|bare}" : all;
    });
    var out = [], last = 0, m;
    TOKEN.lastIndex = 0;
    while ((m = TOKEN.exec(str))) {
      if (m.index > last) out.push(txt(str.slice(last, m.index)));
      if (m[1]) out.push(UI.value(refDatum(m[1]), m[2] || undefined, "prose"));
      else { refDatum(m[3]); out.push(chipFor(m[3])); }
      last = TOKEN.lastIndex;
    }
    if (last < str.length) out.push(txt(str.slice(last)));
    return glue(out);
  }
  /* inside a module view a gap chip is a link to that module's "Gaps and limitations", where the gap is stated once */
  function gapLink(ref) {
    return el("a", { class: "gapref", href: gapHref, "data-ref-link": ref, "aria-label": "Gap " + ref + ", listed under Gaps and limitations" }, [ref]);
  }
  function chipFor(ref) { return gapHref && ref.charAt(0) === "G" ? gapLink(ref) : UI.chip(ref); }
  /* a full stop or comma after a figure button must not wrap onto a line of its own */
  function glue(nodes) {
    for (var i = 1; i < nodes.length; i++) {
      var prev = nodes[i - 1], n = nodes[i];
      if (n.nodeType === 3 && /^[.,;:)]/.test(n.nodeValue) && prev.querySelector && prev.querySelector(".figref")) n.nodeValue = "\u2060" + n.nodeValue;
      else if (n.nodeType === 3 && /^[.,;:)]/.test(n.nodeValue) && prev.nodeType === 11) n.nodeValue = "\u2060" + n.nodeValue;
    }
    return nodes;
  }
  function refsIn(str) {
    var out = [], m;
    TOKEN.lastIndex = 0;
    while ((m = TOKEN.exec(str))) { var r = m[1] || m[3]; if (out.indexOf(r) < 0) out.push(r); }
    return out;
  }
  /* tokens by figure key: tk prints the value (the figure is the button) */
  function tk(key, unit) { if (!F[key]) throw new Error("No figure " + key); return "{" + F[key].ref + (unit ? "|" + unit : "") + "}"; }
  function ck(key) { if (!F[key]) throw new Error("No figure " + key); return "[" + F[key].ref + "]"; }

  /* A model-written item: the text with each cited figure turned into its own button. A cited or calculated
     reference whose value is not in the sentence goes to `sink` (the block's source notes); a gap keeps its n/a mark. */
  function findToken(text, needle, taken) {
    if (!needle) return -1;
    var re = new RegExp("(^|[^0-9A-Za-z.,])(" + needle.replace(/[.*+?^${}()|[\]\\]/g, "\\$&") + ")(?![0-9]|[.,][0-9]|[A-Za-wyz])", "g"), m;
    while ((m = re.exec(text))) {
      var at = m.index + m[1].length;
      if (!taken.some(function (t) { return at < t.end && at + needle.length > t.start; })) return at;
    }
    return -1;
  }
  function itemNodes(item, sink) {
    var text = item.text, taken = [], gaps = [];
    (item.refs || []).forEach(function (r) {
      if (D.gaps[r]) { gaps.push(r); return; }
      var c = D.citations[r] || D.calcs[r], d = refDatum(r), cands = [String(d.v)];
      if (c && cands.indexOf(String(c.value)) < 0) cands.push(String(c.value));
      for (var i = 0; i < cands.length; i++) {
        var at = findToken(text, cands[i], taken);
        if (at >= 0) { taken.push({ start: at, end: at + cands[i].length, ref: r, datum: d }); return; }
      }
      if (sink && sink.indexOf(r) < 0) sink.push(r);
    });
    taken.sort(function (a, b) { return a.start - b.start; });
    var out = [], pos = 0;
    taken.forEach(function (t) {
      if (t.start > pos) out.push(txt(text.slice(pos, t.start)));
      /* money, multiples and percentages print by unit ("US,962m", "3.29x"); a trailing x or % in the sentence belongs to the figure */
      var node = UI.value(t.datum, undefined, "prose"), suffix = text.charAt(t.end);
      var btn = node.querySelector ? node.querySelector(".figref") : null;
      if (btn && (suffix === "x" || suffix === "%")) {
        if (btn.textContent.slice(-1) !== suffix) btn.insertBefore(txt(suffix), btn.querySelector(".hit"));
        t.end += 1;
      }
      out.push(node);
      pos = t.end;
    });
    if (pos < text.length) out.push(txt(text.slice(pos)));
    gaps.forEach(function (g) { out.push(chipFor(g)); });
    return glue(out);
  }
  /* margin notes: the citations a prose block rests on, as an IC paper's side notes */
  function noteValue(r) {
    var d = refDatum(r), f = displayFormat(d, undefined, "table");
    return f === null ? String(d.v) : f;
  }
  function notes(refs) {
    var ol = el("ol", { class: "mnotes", "aria-label": "Sources for this passage" });
    refs.forEach(function (r) {
      var c = D.citations[r], k = D.calcs[r], g = D.gaps[r], src, label, val;
      if (c) { label = c.label; val = noteValue(r); src = c.file + ", " + (c.locator || "line " + c.line); }
      else if (k) { label = k.label; val = noteValue(r); src = k.formula; }
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
  /* a block's cited references that no sentence shows, as one source note under it */
  function sourceNote(refs) {
    if (!refs || !refs.length) return null;
    return el("div", { class: "src-notes src-notes--inline" }, [notes(refs)]);
  }
  function isIllus(node, what) {
    return el("span", { class: "is-illus", title: what + ": illustrative, no RBOT run exists" }, [node, el("span", { class: "vh", text: " (illustrative)" })]);
  }
  function dirChip(word) {
    var w = String(word).toLowerCase();
    var cls = /improving|positive/.test(w) ? "up" : /deteriorating|negative/.test(w) ? "down" : "flat";
    return el("span", { class: "dir dir--" + cls, text: word });
  }
  /* Credit Direction as a call-band item: the same box as the scales (neutral), an arrow for the position */
  function dirBadge(word, label) {
    var w = String(word).toLowerCase();
    var cls = /improving|positive/.test(w) ? "up" : /deteriorating|negative/.test(w) ? "down" : "flat";
    return el("span", { class: "scale scale--lg scale--dir", role: "img", "aria-label": label + ": " + word + ", illustrative" }, [
      el("span", { class: "scale__pos scale__pos--dir dirico--" + cls, "aria-hidden": "true" }), el("span", { class: "scale__word", "aria-hidden": "true", text: word })]);
  }
  function scaleRec(r, label, size) { return UI.scale({ kind: "rec", pos: r.pos, word: r.word, illustrative: true, label: label, size: size }); }
  function modelTag() { return el("span", { class: "tag-model", text: "Model" }); }

  /* ------------------------------------------------------------ tables */
  function th(label, unit, num) {
    return el("th", { scope: "col", class: num ? "num" : null }, [label, unit ? el("span", { class: "unit", text: unit }) : null]);
  }
  function tdD(d, opts) {
    var c = el("td", { class: opts && opts.text ? null : "num" });
    UI.cell(c, d, opts && opts.unit, opts && opts.kind);
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
  /* align: the column labels of a sibling table; a period this table lacks leaves a blank cell so the columns line up */
  function periodTable(t, filter, caption, cls, align) {
    var order = align || t.columns;
    var cols = [th(t.unit === "x" ? "Multiple (x)" : t.unit || "")].concat(order.map(function (c) {
      return t.columns.indexOf(c) < 0 ? el("th", { class: "blank", "aria-hidden": "true" }) : th(c, null, true);
    }));
    var rows = t.rows.filter(filter || function () { return true; }).map(function (r) {
      var row = el("tr", { class: kindClass(r.kind) }, [rowTh(r.label)]);
      order.forEach(function (c) {
        var i = t.columns.indexOf(c);
        row.appendChild(i < 0 ? el("td", { class: "blank", "aria-hidden": "true" }) : tdD(r.cells[i]));
      });
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
  /* sub-headings follow the section above them (h3 under an h2 section, h4 under an h3 one) */
  function subh(text, extra) { return el("h" + subLevel, { class: "subh" }, [text].concat(extra || [])); }

  /* ------------------------------------------------------------ figures (numbered once across the whole Report) */
  /* "Fig. CP-1.2": numbered by the label the pane shows (S Snapshot, CP-n a module, M Model, PF Portfolio Fit, E Evidence);
     a figure drawn again in another view keeps its first number */
  function figLabel(base) {
    if (!FIGS[base]) { figCount[curPre] = (figCount[curPre] || 0) + 1; FIGS[base] = "Fig. " + curPre + "." + figCount[curPre]; }
    return FIGS[base];
  }
  function draw(kind, host, spec, over) {
    var base = (over && over.id) || spec.id || ("fig-" + (figCount[curPre] || 0));
    var sp = Object.assign({}, spec, { number: figLabel(base), headingLevel: subLevel }, over || {});
    sp.id = curView + "--" + base;
    charts.push(C[kind](host, sp));
    return FIGS[base];
  }
  /* A figure the data cannot draw: the frame, its title and the missing input with its reason. */
  function naFigure(host, o) {
    var label = figLabel(o.id), id = curView + "--" + o.id;
    var reasons = el("span", {}, []);
    o.refs.forEach(function (r) { reasons.appendChild(UI.chip(r)); });
    host.appendChild(el("figure", { class: "chart chart--na", id: id }, [
      el("div", { class: "chart__head" }, [el("span", { class: "chart__num", text: label }),
        el("h" + subLevel, { class: "chart__title", text: o.title }), el("p", { class: "chart__summary", text: o.summary })]),
      el("div", { class: "chart__plot", role: "img", "aria-label": o.title + ": not drawn, " + o.missing }, [
        el("p", { class: "chart__na" }, [el("b", { text: "n/a: not drawn" }), txt(o.missing + " "), reasons])]),
      el("p", { class: "chart__source", text: "Source: " + o.source })
    ]));
  }
  function figHost(parent) { var h = el("div", { class: "figbox" }); parent.appendChild(h); return h; }

  /* ------------------------------------------------------------ collapsible blocks */
  /* One affordance everywhere: a bar with a chevron, the title and tags. The state is also written in words
     ("Collapse" / "Expand"). A "Full analysis" link sits on the block's footer line, never inside the toggle. */
  function cb(parent, o) {
    var tags = [];
    if (o.illus) tags.push(UI.illus());
    if (o.synth) tags.push(el("span", { class: "synth", text: "Synthetic" }));
    if (o.model) tags.push(modelTag());
    var head = el("summary", {}, [
      el("h" + (o.level || 2), { class: "cb__t", id: o.id ? o.id + "-h" : null }, [o.title]),
      el("span", { class: "cb__meta" }, o.meta || []),
      tags.length ? el("span", { class: o.paper ? "cb__tags" : "cb__tags on-navy" }, tags) : null
    ]);
    var body = el("div", { class: "cb__body" + (o.flush ? " cb__body--flush" : "") });
    var d = el("details", { class: "cb " + (o.paper ? "cb--paper " : "") + (o.model ? "cb--model " : "") + (o.cls || ""), id: o.id || null }, [head, body]);
    d.open = o.open !== false;
    if (o.keep) d.setAttribute("data-keep", "1");
    if (o.nav === false) d.setAttribute("data-nav", "skip");
    if (o.search === false) d.setAttribute("data-search", "skip");
    if (o.short) d.setAttribute("data-short", o.short);
    parent.appendChild(d);
    if (o.full || o.foot) {
      d.appendChild(el("div", { class: "cb__foot" }, [
        el("p", { class: "cb__src" }, o.foot || []),
        o.full ? el("a", { class: "cb__full", href: o.full, "aria-label": "Full analysis of " + o.title }, ["Full analysis"]) : null
      ]));
    }
    return body;
  }
  function viewTools(v) {
    var b = el("button", { type: "button", class: "btn btn--quiet vtools", text: "Collapse all" });
    function boxes() { return Array.prototype.filter.call(v.el.querySelectorAll("details.cb"), function (d) { return !d.hasAttribute("data-keep"); }); }
    function sync() {
      b.textContent = boxes().some(function (d) { return d.open; }) ? "Collapse all" : "Expand all";
    }
    b.addEventListener("click", function () {
      var all = boxes(), any = all.some(function (d) { return d.open; });
      all.forEach(function (d) { d.open = !any; });
      sync();
    });
    v.el.addEventListener("toggle", sync, true);
    return b;
  }

  /* ------------------------------------------------------------ views */
  function newView(id, o) {
    curView = id; curPre = o.pre; PRE[id] = o.pre; subLevel = 3;
    var h1 = el("h1", { class: "vtitle", tabindex: "-1" }, o.h1 || o.title);
    var v = { id: id, title: o.title, group: o.group || null, el: null, h1: h1, nav: null, toc: [] };
    v.el = el("article", { class: "view" + (o.cls ? " " + o.cls : ""), id: "view-" + id, "data-view": id, "aria-labelledby": "view-" + id + "-h" });
    h1.id = "view-" + id + "-h";
    v.el.hidden = true;
    VIEWS[id] = v; ORDER.push(id);
    main.appendChild(v.el);
    v.tools = viewTools(v);
    v.bar = el("div", { class: "vbar" }, [keyButton(), v.tools]);
    return v;
  }
  function plainHead(v, lede, code) {
    var top = el("div", { class: "vhead__top" }, [v.h1, code ? el("span", { class: "vhead__code", title: "RBOT module code", text: code }) : null, v.bar]);
    var hd = el("header", { class: "vhead" }, [top, lede ? el("p", { class: "vhead__lede" }, lede) : null]);
    v.el.appendChild(hd);
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
  /* the module whose content joins another view: one door each (CP-5 into Evidence, CP-6 into Portfolio Fit) */
  var FOLD_INTO = { qa: "evidence", fit: "portfolio-fit" };
  function foldOf(m) { var t = topicOf(m); return t && FOLD_INTO[t] ? FOLD_INTO[t] : null; }
  var NAV_MODS = MODS.filter(function (m) { return !foldOf(m); });
  /* "Full analysis" target: the section of the module view that owns a topic */
  function fullLink(topic, part) {
    var m = hostOf(topic);
    return m ? "#" + (part ? slug(m.id) + "-" + part : modId(m)) : null;
  }
  /* reader-facing names: plain words, glossary terms; the pipeline code stays a small secondary label */
  var PLAIN_NAME = { intake: "Source readiness", qa: "Evidence checks", fit: "Sector weights and fit summary" };
  function plainName(m) { var t = topicOf(m); return (t && PLAIN_NAME[t]) || m.name.replace(/\s*\(Test CLO I\)$/, ""); }

  /* the operating model at summary size: one sentence and five cited facts */
  function opmSentence() {
    return rich("Caesars is a " + tk("opm_description") + ", founded in " + tk("opm_founded") + "; its primary source of revenue is " + tk("opm_revenue_source") + ".");
  }
  function opmFacts() {
    var share = function (s) { return tk("opm_seg_share_" + s + "_fy2025", "%"); };
    return [
      ["Segments", "Regional " + share("regional") + ", Las Vegas " + share("las_vegas") + ", Caesars Digital " + share("caesars_digital") + " and Managed and Branded " +
        share("managed_branded") + " of FY2025 net revenues of " + tk("net_revenues_fy2025", "US$ m")],
      ["Revenue mix", "Casino about " + tk("opm_casino_share_fy2025", "%") + ", hotel " + tk("opm_hotel_share_fy2025", "%") + " and food and beverage " + tk("opm_fb_share_fy2025", "%") + " of FY2025 net revenues"],
      ["Footprint", tk("opm_properties") + " properties in " + tk("opm_jurisdictions") + " jurisdictions at 30 June 2026"],
      ["Real estate", tk("opm_owned_casinos") + " casinos owned and " + tk("opm_leased_casinos") + " leased: " + tk("opm_vici_casinos") + " from VICI, " + tk("opm_glpi_casinos") +
        " from GLPI and Caesars Windsor from the " + tk("opm_windsor")],
      ["Digital", "Sports wagering in " + tk("opm_sports_jurisdictions") + " jurisdictions, " + tk("opm_online_sports_jurisdictions") + " online; iGaming in " + tk("opm_igaming_jurisdictions")]
    ].map(function (r) { return [r[0], rich(r[1])]; });
  }
  function opmParagraphs() {
    var seg = function (s) { return tk("opm_seg_rev_" + s + "_fy2025", "US$ m"); };
    var share = function (s) { return tk("opm_seg_share_" + s + "_fy2025", "%"); };
    var p = [
      "Caesars is a " + tk("opm_description") + ", founded in " + tk("opm_founded") + ". Its primary source of revenue is " + tk("opm_revenue_source") + ".",
      "It reports " + tk("opm_segments_count") + ": Las Vegas, Regional, Caesars Digital, and Managed and Branded. FY2025 net revenues of " + tk("net_revenues_fy2025", "US$ m") +
        " came from Regional at " + seg("regional") + " (" + share("regional") + " of the total), Las Vegas at " + seg("las_vegas") + " (" + share("las_vegas") +
        "), Caesars Digital at " + seg("caesars_digital") + " and Managed and Branded at " + seg("managed_branded") + ", which earns " + tk("opm_mb_fees") +
        " for managing other hotels and casinos. By type, casino was approximately " + tk("opm_casino_share_fy2025", "%") + " of net revenues, hotel " + tk("opm_hotel_share_fy2025", "%") +
        " and food and beverage " + tk("opm_fb_share_fy2025", "%") + ".",
      "At 30 June 2026 it owned, leased or managed " + tk("opm_properties") + " properties in " + tk("opm_jurisdictions") + " jurisdictions. It owned " + tk("opm_owned_casinos") +
        " of its casinos and leased " + tk("opm_leased_casinos") + ": " + tk("opm_vici_casinos") + " from VICI, " + tk("opm_glpi_casinos") + " from GLPI and Caesars Windsor from the " + tk("opm_windsor") +
        ". The VICI and GLPI leases are financing obligations of " + tk("opm_vici_obligation") + " and " + tk("opm_glpi_obligation") + " at 31 December 2025, and " +
        tk("lt_financing_obligations_2026_06_30", "US$ m") + " at 30 June 2026, shown apart from reported debt.",
      "Caesars Digital operates sports wagering across " + tk("opm_sports_jurisdictions") + " jurisdictions, " + tk("opm_online_sports_jurisdictions") + " of them online, and iGaming in " +
        tk("opm_igaming_jurisdictions") + "."
    ];
    return p.map(function (s) { return el("p", { class: "desc__p" }, rich(s)); });
  }

  /* Portfolio Fit and the instrument to own, from the data: the PM must not walk in without the CLO flag */
  function fitSummary() {
    var fit = P.fit, name = String(fit.portfolio).replace(/ Ltd$/, "");
    var breach = fit.byInstrument.filter(function (b) { return /^breach/i.test(b.fit); });
    var breaches = breach.map(function (b) {
      var m = /(\d+(?:\.\d+)?%).*?(\d{4})$/.exec(b.instrument), lim = /(CCC bucket)/.exec(b.note || "");
      return (m ? m[1] + " " + m[2] + "s" : b.instrument) + " would breach " + (lim ? "the " + lim[1] : "a limit");
    });
    var parts = [];
    fit.checks.filter(function (c) { return c.result === "Watch"; }).forEach(function (c) {
      var lim = c.constraint.replace(/^C-\d+\s*/, "").replace(/^Max /, "").toLowerCase();
      if (breaches.join(" ").toLowerCase().indexOf(lim) >= 0) return;
      parts.push(lim + " has " + c.headroom + " headroom");
    });
    return { name: name, overall: fit.overall.v, breaches: breaches, text: parts.join("; ") };
  }
  function fitNodes(fs) {
    var out = [el("b", { text: fs.name + ": " }), nw([UI.status(fs.overall)]), txt(" overall. ")];
    fs.breaches.forEach(function (t) { out.push(nw([UI.status("Breaches"), txt(" " + t)]), txt(". ")); });
    if (fs.text) out.push(txt(fs.text.charAt(0).toUpperCase() + fs.text.slice(1) + ". "));
    out.push(el("a", { class: "call__more nowrap", href: "#portfolio-fit", text: "Details in Portfolio Fit" }), txt(" "), nw([el("span", { class: "synth", text: "Synthetic" })]));
    return out;
  }
  function nw(nodes) { return el("span", { class: "nowrap" }, nodes); }
  /* the instrument preference names its Strategy and, where Portfolio Fit flags that instrument, says so */
  function instrumentLine(fs) {
    var pref = preferenceSentence();
    if (!pref) return null;
    var strat = M.strategies.filter(function (x) { return /HY|bond/i.test(x); })[0] || M.strategies[M.strategies.length - 1];
    var flagged = P.fit.byInstrument.filter(function (b) {
      return /secured/i.test(b.instrument) && !/unsecured/i.test(b.instrument) && /2032/.test(b.instrument) && !/^fits/i.test(b.fit);
    })[0];
    var pw = pref.replace(/\s+$/, "").split(" "), last = pw.pop();
    var nodes = [el("b", { text: strat + ": " }), txt(pw.join(" ") + " "), nw([txt(last + " "), UI.illus()])];
    if (flagged) {
      var elig = /eligible CLO asset/i.test(flagged.note || "") ? "CLO eligibility unknown" : String(flagged.note || "flagged").replace(/\.$/, "");
      var im = /(\d+(?:\.\d+)?%).*?(\d{4})$/.exec(flagged.instrument), iname = im ? im[1] + " secured " + im[2] + "s" : String(flagged.instrument);
      nodes.push(txt(" "), nw([UI.status(flagged.fit), txt(" " + iname + ": " + elig)]), txt("; "),
        el("a", { class: "call__more nowrap", href: "#portfolio-fit-instrument", text: "see Portfolio Fit" }), txt(" "), nw([el("span", { class: "synth", text: "Synthetic" })]));
    }
    return nodes;
  }
  function preferenceSentence() {
    var s = String(I.thesis.text).split(/(?<=\.)\s+/).filter(function (x) { return /^Prefer\b/.test(x); })[0];
    return s || null;
  }

  function buildSnapshot() {
    var v = newView("snapshot", { title: "Snapshot", h1: M.issuer.replace(/, Inc\.$/, "") + " (" + M.ticker + ")", cls: "view--snapshot", pre: "S" });
    var s = v.el;

    /* title band: the issuer, then the call */
    var meta = el("p", { class: "titleband__meta" }, [
      el("span", { text: "Credit Snapshot" }),
      el("span", { text: M.pathway + ", " + M.depth + " depth" }),
      M.primary ? el("span", { text: M.primaryLabel }) : null,
      el("span", { text: M.reportingPeriod }),
      el("span", { text: M.runId ? "Run " + M.runId : M.runNote })
    ]);
    var call = el("div", { class: "call on-navy", role: "group", "aria-label": "Analyst recommendation, illustrative" }, [
      el("div", { class: "call__label" }, [el("span", { class: "call__title" }, ["Analyst recommendation", UI.illus()]),
        el("span", { class: "call__who" }, [txt("By " + String(M.analyst.v).replace(/ \(illustrative\)/i, "") + " · "), el("span", { class: "num", text: M.analysisDate })])])
    ]);
    var cells = el("div", { class: "call__cells" });
    call.appendChild(cells);
    M.strategies.forEach(function (st) {
      cells.appendChild(el("span", { class: "call__item" }, [el("span", { class: "call__k", text: st }), scaleRec(I.recommendation[st], st, "lg")]));
    });
    cells.appendChild(el("span", { class: "call__item call__item--first" }, [el("span", { class: "call__k", text: "Valuation" }),
      UI.scale({ kind: "val", pos: I.valuation.pos, illustrative: true, label: "Valuation", size: "lg" })]));
    cells.appendChild(el("span", { class: "call__item" }, [el("span", { class: "call__k", text: "Credit Score" }),
      UI.scale({ kind: "score", pos: I.creditScore.pos, word: I.creditScore.word, illustrative: true, label: "Credit Score", size: "lg" })]));
    cells.appendChild(el("span", { class: "call__item" }, [el("span", { class: "call__k", text: "Credit Direction" }), dirBadge(I.creditDirection.word, "Credit Direction")]));
    var fs = fitSummary(), ins = instrumentLine(fs);
    var lines = el("div", { class: "call__lines" }, [
      el("p", { class: "call__line" }, [el("span", { class: "call__lk", text: "Portfolio Fit" }),
        el("span", { class: "call__lv" }, fitNodes(fs))]),
      ins ? el("p", { class: "call__line" }, [el("span", { class: "call__lk", text: "Instrument" }), el("span", { class: "call__lv" }, ins)]) : null
    ]);
    call.appendChild(lines);
    var toc = el("div", { class: "toc-slot" });
    v.tocSlot = toc;
    s.appendChild(el("header", { class: "titleband" }, [el("div", { class: "titleband__top" }, [v.h1, v.bar]), meta, toc, call]));

    var fp = el("div", { class: "fp" });
    s.appendChild(fp);

    /* Key findings and the main risk | the operating model at summary size */
    var sink = [];
    var kf = cb(fp, { title: "Key findings", id: "key-findings", cls: "span-5 p-kf", model: true, flush: true, keep: true });
    kf.appendChild(el("ol", { class: "kf" }, I.keyFindings.map(function (f) { return el("li", {}, [el("span", {}, itemNodes(f, sink))]); })));
    var risk = I.weaknesses[0];
    kf.appendChild(el("p", { class: "kf__thesis" }, [el("b", { text: "Main risk: " + risk.label + ". " })].concat(itemNodes(risk, sink))));
    var kfn = sourceNote(sink);
    if (kfn) kf.appendChild(el("details", { class: "srcs" }, [el("summary", { text: "Sources for these findings (" + sink.length + ")" }), kfn]));

    var co = cb(fp, { title: "Company and operating model", short: "Company", id: "company", cls: "span-7 p-co", flush: true, full: fullLink("business", "business"),
      foot: ["Sources: FY2025 10-K and Q2 2026 10-Q."] });
    co.appendChild(el("p", { class: "co__lede" }, opmSentence()));
    co.appendChild(el("table", { class: "dt dt--kv opm" }, [el("caption", { class: "vh", text: "Operating model" }),
      el("tbody", {}, opmFacts().map(function (r) { return el("tr", {}, [rowTh(r[0]), el("td", {}, r[1])]); }))]));

    /* Figures: the Model chart strip */
    var fb = cb(fp, { title: "Model chart strip", short: "Charts", id: "figures", cls: "span-12 p-figs", flush: true, full: "#model-credit-metrics",
      meta: ["Select any mark for its source"],
      foot: [txt("Sources: Caesars FY2025 10-K and Q2 2026 10-Q; leverage, coverage and liquidity calculated from cited figures. Maturity wall: face value at final maturity, by instrument; the 10-Q annual maturities table, which includes amortisation, shows ")]
        .concat(rich("{C182|US$ m}"), [txt(" for 2030. n/a: not in the sources; select it for the reason.")]) });
    var row = el("div", { class: "figrow" });
    fb.appendChild(row);
    [["lineStrip", K.leverage, 126], ["lineStrip", K.coverage, 126], ["lineStrip", K.liquidity, 126], ["stackedColumns", K.maturityWall, 108]].forEach(function (p) {
      var cell = el("div", { class: "figcell" });
      row.appendChild(cell);
      /* the strip cells are narrow: short year labels keep the axis clear at 12px */
      draw(p[0], cell, p[1], { height: p[2], ticks: 3, minWidth: 120, categories: p[1].categories.map(function (c) { return String(c).replace(/^FY20(\d\d)$/, "FY$1"); }) });
    });

    /* Capital structure summary | EBITDA adjustments summary */
    var cap = cb(fp, { title: "Capital structure", id: "capital-structure", cls: "span-7 p-cap", flush: true, full: fullLink("financials", "capital-structure"),
      meta: ["At " + T.capitalStructure.asOf + "; x LTM Adjusted EBITDA"] });
    cap.appendChild(capSummary());
    cap.appendChild(srcNote("", rich("EBITDA basis: " + T.capitalStructure.ebitda_basis + ". Financing obligations to GLPI and VICI of {C184|US$ m} are shown apart from debt.")));
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
    fl.appendChild(periodTable(T.financials, pick(T.financials, ["Revenue", "EBITDA (Adjusted, company-defined)", "% margin", "FCF"]), "Financials summary", "pt--six wraphead"));
    fl.appendChild(periodTable(T.creditMetrics, pick(T.creditMetrics, ["Total Leverage", "Net Leverage", "Interest Cover"]), "Credit metrics summary", "pt--four wraphead", T.financials.columns));
    var fr = el("div", { class: "finbox__chart" });
    fg.appendChild(fr);
    draw("columns", fr, K.revenueEbitda, { height: 170 });

    /* Strengths and weaknesses */
    var sink2 = [];
    var sw = cb(fp, { title: "Strengths and weaknesses", short: "Strengths and weaknesses", id: "credit-summary", cls: "span-12 p-sw", illus: true, model: true, flush: true, full: fullLink("rv", "credit-view") });
    sw.appendChild(el("p", { class: "sw__thesis" }, [el("span", { class: "sw__t" }, [el("b", { text: "Thesis. " })].concat(itemNodes(I.thesis, sink2)))]));
    sw.appendChild(el("div", { class: "swgrid" }, [
      el("div", {}, [el("div", { class: "bar bar--sub", text: "Strengths" }), swRows(I.strengths, sink2)]),
      el("div", {}, [el("div", { class: "bar bar--sub", text: "Weaknesses" }), swRows(I.weaknesses, sink2)])
    ]));
    var swn = sourceNote(sink2);
    if (swn) sw.appendChild(el("details", { class: "srcs" }, [el("summary", { text: "Sources for the thesis (" + sink2.length + ")" }), swn]));

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
      var sink3 = [];
      var tx = cb(fp, { title: "Transaction summary and new debt issues", short: "Transaction", id: "transaction", cls: "span-12 p-tx", model: true, flush: true, open: false, full: fullLink("business", "business"),
        meta: [M.primaryLabel] });
      tx.appendChild(el("div", { class: "tx__text" }, [el("p", {}, itemNodes(I.transactionSummary, sink3))]));
      tx.appendChild(newDebtTable());
      var txn = sourceNote(sink3);
      if (txn) tx.appendChild(txn);
    }

    /* the questions this paper expects at committee, last: they point at the module that works them through */
    var ccb = cb(fp, { title: "Committee challenge", id: "committee-challenge", cls: "span-12 p-cc", illus: true, model: true, flush: true, full: fullLink("challenge", "challenge") });
    ccb.appendChild(el("ol", { class: "kf kf--one cq" }, QUESTIONS.map(function (q) { return el("li", {}, [el("span", {}, rich(q))]); })));
  }

  function swRows(list, sink) {
    return el("table", { class: "dt sw" }, [el("tbody", {}, list.map(function (w) {
      return el("tr", {}, [rowTh(w.label), el("td", {}, itemNodes(w, sink))]);
    }))]);
  }
  function profileTable() {
    var cells = [
      ["Ticker", [UI.value(fd("issuer.ticker"), undefined, "prose")]],
      ["Management", [txt("CEO "), UI.value(fd("issuer.ceo"), undefined, "prose"), txt(", CFO "), UI.value(fd("issuer.cfo"), undefined, "prose")]],
      ["Credit Score", [isIllus(UI.scale({ kind: "score", pos: I.creditScore.pos, word: I.creditScore.word, illustrative: true, label: "Credit Score" }), "Credit Score")]],
      ["Morningstar Issuer ID", [UI.value(gapD("G24"))]],
      ["Sector Outlook", [isIllus(dirChip(I.sectorOutlook.word), "Sector Outlook")]],
      ["Credit Direction", [isIllus(dirChip(I.creditDirection.word), "Credit Direction")]],
      ["Sector / Country", [UI.value(gapD(null, "sector and country of domicile are not among the extracted figures"))]],
      ["Sponsor Quality", [isIllus(el("span", { class: "prov-model", title: I.sponsorQuality.basis, text: I.sponsorQuality.word }), "Sponsor Quality")]],
      ["Issue ratings (M/S)", [txt("SS 2032s "), UI.value(fd("trace_czr_12769gac4_moodys"), undefined, "prose"), txt(" / "), UI.value(fd("trace_czr_12769gac4_sp"), undefined, "prose")]],
      ["Shareholders", [txt("Listed; merger agreed with "), UI.value(fd("issuer.merger.acquirer_brand"), undefined, "prose")]],
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
    return table("New debt issues", [th("Borrower"), th("Bloomberg ID (FIGI)"), th("Instrument"), th("Debt type"), th("Use of proceeds"),
      th("Tranche size", "US$ m", true), th("Price Talk"), th("OID"), th("Maturity"), th("Exp. ratings"), th("CR Score"), th("Commit date")], [
      el("tr", {}, [tdD(g8, { text: true }), tdD(gapD("G28"), { text: true }),
        tdN([txt("New debt from "), UI.value(fd("merger_financing_banks_count"), undefined, "prose"), txt(" banks")], "nowrap"), tdD(g8, { text: true }),
        tdD({ v: "Acquisition", prov: "cited", ref: "C12" }, { text: true }),
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
      if (rs.length) line(rankLabel(rank) + " (" + rs.length + (rs.length === 1 ? " facility" : " facilities") + ")", rankAmount(rank, sub), rs[rs.length - 1], "sub");
    });
    line("Total debt", sub.total_debt, cs.rows[cs.rows.length - 1], "total");
    line("Cash", sub.cash, null, "sub");
    line("Net debt", sub.net_debt, null, "total");
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
      rows.push(el("tr", { class: "indent" }, [rowTh(r.facility), tdD(r.figi, { text: true }), tdD(r.ratings, { text: true }), tdD(r.coupon, { kind: "rate" }),
        el("td", { text: r.ccy }), nowrap(tdD(r.maturity, { text: true })), bid, ask, tdD(r.outstanding), tdD(r.structuring_multiple), tdD(r.ssim_multiple), tdD(r.pct_ev),
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
    subtotal("Net debt", sub.net_debt, null, "total");
    subtotal("(Implied) equity, at the merger value", sub.implied_equity, null, "sub");
    rows.push(el("tr", { class: "total" }, [el("th", { scope: "row", colspan: "8", style: "text-align:right", text: "EV (merger transaction value) and EV multiple" }),
      tdD(sub.ev), tdD(sub.ev_multiple), el("td"), el("td"), el("td")]));
    rows.push(el("tr", { class: "sub" }, [el("th", { scope: "row", colspan: "8", style: "text-align:right", text: "Equity market value" }), tdD(sub.equity_market_value), el("td"), el("td"), el("td"), el("td")]));
    rows.push(el("tr", { class: "sub" }, [el("th", { scope: "row", colspan: "8", style: "text-align:right", text: "PF interest" }), tdD(sub.pf_interest), el("td"), el("td"), el("td"), el("td")]));
    return table("Capital structure at " + cs.asOf, cols, rows, "captab wraphead");
  }

  var INDEX_GAP = "Bloomberg index statistics are not in the Source Pack";
  var BOND_SIZES = { "12769GAC4": "CEI 6.50% Senior Secured Notes 2032", "12769GAD2": "CEI 6.00% Senior Notes 2032" };
  function capByFacility() {
    var capBy = {};
    T.capitalStructure.rows.forEach(function (r) { capBy[r.facility] = r; });
    return capBy;
  }
  function rvSummary() {
    var capBy = capByFacility();
    return table("Comparable bonds, summary", [th("Company"), th("CUSIP"), th("Seniority"), th("Coupon", "%", true), th("Maturity"), th("Size", "US$ m", true),
      th("Last price", null, true), th("Last yield", "%", true)], T.trace.rows.map(function (r) {
      var capRow = capBy[BOND_SIZES[r.cusip]];
      return el("tr", {}, [rowTh(r.issuer), el("td", { class: "num", text: r.cusip }), nowrap(el("td", { text: r.seniority })), tdD(r.coupon, { kind: "rate" }), nowrap(tdD(r.maturity, { text: true })),
        tdD(capRow ? capRow.outstanding : gapD(null, "peer issue size is not among the extracted figures")), tdD(r.price, { kind: "price" }), tdD(r.yield, { kind: "rate" })]);
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
    wrap.appendChild(table("Comparable loans", [th("Company"), th("Facility"), th("FIGI"), th("Ratings"), th("Size", "US$ m", true), th("Maturity"), th("Seniority")],
      loans.map(function (r) {
        return el("tr", {}, [rowTh(M.ticker), el("td", { text: r.facility }), tdD(r.figi, { text: true }), tdD(r.ratings, { text: true }), tdD(r.outstanding),
          nowrap(tdD(r.maturity, { text: true })), el("td", { text: r.debtType })]);
      }).concat([el("tr", { class: "sub" }, [el("th", { scope: "row", colspan: "7" }, [txt("Peer loans: "), UI.value(gapD("G18"))])])]), "wraphead"));
    wrap.appendChild(el("p", { class: "na-note pad" }, [txt("Margin, mid price, 1M and YTD change, mid YTM and mid 3Y DM are n/a for every loan: "), UI.value(g18)]));
    return wrap;
  }
  function hyRv() {
    var wrap = el("div");
    wrap.appendChild(table("High-yield index statistics", [th("Index rating bucket"), th("Bloomberg ID"), th("Avg coupon", "%", true), th("Market value", "US$ bn", true),
      th("Avg price", null, true), th("Δ 1M", null, true), th("Δ YTD", null, true), th("YTW", "%", true), th("OAS", "bp", true)], [
      el("tr", {}, [rowTh("Ba · Ba/B · B · Caa"), el("td", { colspan: "8" }, [UI.value(gapD(null, INDEX_GAP))])])
    ]));
    var capBy = capByFacility();
    wrap.appendChild(table("Comparable bonds", [th("Company"), th("CUSIP"), th("Moody's"), th("S&P"), th("Size", "US$ m", true), th("Coupon", "%", true),
      th("Maturity"), th("Next call"), th("Seniority"), th("Last price", null, true), th("Last yield", "%", true)],
      T.trace.rows.map(function (r) {
        var capRow = capBy[BOND_SIZES[r.cusip]];
        return el("tr", {}, [rowTh(r.issuer), el("td", { class: "num", text: r.cusip }),
          tdD(r.moodys, { text: true }), tdD(r.sp, { text: true }), tdD(capRow ? capRow.outstanding : gapD(null, "peer issue size is not among the extracted figures")),
          tdD(r.coupon, { kind: "rate" }), nowrap(tdD(r.maturity, { text: true })), nowrap(tdD(r.next_call, { text: true })), nowrap(el("td", { text: r.seniority })), tdD(r.price, { kind: "price" }),
          tdD(r.yield, { kind: "rate" })]);
      }), "wraphead"));
    wrap.appendChild(el("p", { class: "na-note pad" }, [txt("FIGI, 1M and YTD price change and OAS are n/a for every bond: "), UI.value(gapD("G28")), txt(" "), UI.value(gapD(null, "price history is not in the sources; TRACE pages give the last trade only")), txt(" "), UI.value(gapD("G19"))]));
    return wrap;
  }

  /* ================================================================ 2. MODULE VIEWS */
  function docs() {
    var by = {};
    Object.keys(D.citations).forEach(function (id) { var c = D.citations[id]; by[c.file] = (by[c.file] || 0) + 1; });
    return Object.keys(by).map(function (f) { return { file: f, n: by[f], synthetic: /Test_CLO/.test(f) }; });
  }
  function gapTable(refs, caption) {
    return table(caption, [th("Gap"), th("Missing item"), th("Reason")], refs.map(function (r) {
      var g = D.gaps[r];
      return el("tr", {}, [el("th", { scope: "row" }, [UI.chip(r)]), el("td", { text: human(g.field) }), el("td", { text: cap(g.reason) })]);
    }));
  }
  /* label / value / as-at rows, every value a cited or calculated figure shown by its unit */
  function figKv(caption, keys, withPeriod) {
    return el("div", { class: "table-scroll" }, [el("table", { class: "dt dt--kv dt--framed" }, [el("caption", { class: "vh", text: caption }), el("tbody", {}, keys.map(function (k) {
      var vtd = el("td", {}, [UI.value(fd(k), undefined, "figure")]);
      return el("tr", {}, [rowTh(F[k].label.charAt(0).toUpperCase() + F[k].label.slice(1)), vtd,
        withPeriod ? el("td", { class: "kv__when", text: (F[k].period || "").replace(/^as of /, "") }) : null]);
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
  /* one tag for the block (ILLUSTRATIVE in the heading), not one per row */
  function scoresTable() {
    return kvTable("Scores and valuation", [
      ["Credit Score", [UI.scale({ kind: "score", pos: I.creditScore.pos, word: I.creditScore.word, illustrative: true, label: "Credit Score" })]],
      ["Valuation", [UI.scale({ kind: "val", pos: I.valuation.pos, illustrative: true, label: "Valuation" })]],
      ["Credit Direction", [dirChip(I.creditDirection.word)]],
      ["Sector Outlook", [dirChip(I.sectorOutlook.word)]],
      ["Sponsor Quality", [el("span", { text: I.sponsorQuality.word + ". " + I.sponsorQuality.basis })]]
    ].concat(M.strategies.map(function (st) { return [st, [scaleRec(I.recommendation[st], st)]]; })));
  }

  /* operating model in full: the content of the business section of CP-1 */
  function operatingModelFull(body) {
    opmParagraphs().forEach(function (p) { body.appendChild(p); });
    body.appendChild(subh("Segments, FY2025"));
    body.appendChild(periodTable(OM.segments, null, null, "wraphead"));
    body.appendChild(srcNote(OM.segments.note));
    var pair = el("div", { class: "figpair" });
    body.appendChild(pair);
    var a = figHost(pair), b = figHost(pair);
    a.appendChild(subh("Net revenues by type"));
    a.appendChild(periodTable(OM.revenueType, null, null, "wraphead"));
    draw("stackedColumns", b, K.segmentMix, { height: 230 });
    body.appendChild(srcNote("", [txt(K.segmentMix.note)]));
    var two = el("div", { class: "figpair" });
    body.appendChild(two);
    var re = figHost(two), dg = figHost(two);
    re.appendChild(subh("Owned versus leased real estate"));
    re.appendChild(figKv("Owned versus leased real estate", ["opm_owned_casinos", "opm_leased_casinos", "opm_vici_casinos", "opm_glpi_casinos", "opm_windsor",
      "opm_vici_term", "opm_vici_rent", "opm_vici_obligation", "opm_glpi_term", "opm_glpi_obligation", "lt_financing_obligations_2026_06_30"], true));
    dg.appendChild(subh("Digital"));
    dg.appendChild(figKv("Digital footprint", ["opm_sports_jurisdictions", "opm_online_sports_jurisdictions", "opm_igaming_jurisdictions", "opm_racebook_states"], true));
    body.appendChild(el("p", { class: "na-note", text: "Not stated in the filings as a count and so left out: properties per segment (the 10-K lists them by name), and the owned or leased status of each property by segment." }));
  }

  /* Topics carry the content; modules from RBOT_DATA decide which topics get their own view.
     A topic whose module is not in this run's module list joins its host module's view. */
  var QUESTIONS = [
    "Would the secured 2032s hold value if the merger adds debt of unknown size [G8]?",
    "Is the fall in Las Vegas Adjusted EBITDA to {C94|US$ m} from {C95|US$ m} cyclical or structural?",
    "Do the financing obligations to GLPI and VICI of {C184|US$ m}, which sit outside reported debt, belong in leverage?"
  ];
  var TOPICS = {
    intake: {
      title: "Source readiness", ledeTitle: "Gaps raised before the run", detailTitle: "Documents admitted",
      headline: function () {
        var n = docs().filter(function (d) { return !d.synthetic; }).length;
        return n + " issuer, market and peer documents are admitted into the Source Pack, and every figure drawn from them carries a file and line; what is missing is listed under Gaps and limitations.";
      },
      lede: null,
      detail: function (body) { body.appendChild(docTable()); }
    },
    financials: {
      title: "Financial analysis and capital structure", ledeTitle: "Debt stack", detailTitle: "Credit metrics and balance sheet",
      headline: "LTM Adjusted EBITDA of {K2|US$ m} on net revenues of {K1|US$ m}; total debt of {C114|US$ m} puts total leverage at {K55|x} and net leverage at {K56|x}, before any merger debt [G8].",
      lede: function (host) {
        var sub = T.capitalStructure.subtotals;
        draw("waterfall", host, {
          id: "fig-debt-stack", title: "Debt stack by rank, 30 June 2026", unit: "US$ m", categoryLabel: "Rank", stepLabel: "Debt by rank",
          summary: "Senior secured " + sub.senior_secured.v + ", unsecured " + sub.unsecured.v + " and other " + sub.other.v + " make total debt of " + sub.total_debt.v + " at face value.",
          steps: [{ label: "Senior secured debt", short: "Secured", kind: "delta", d: sub.senior_secured },
            { label: "Unsecured debt", short: "Unsecured", kind: "delta", d: sub.unsecured },
            { label: "Other debt", short: "Other", kind: "delta", d: sub.other },
            { label: "Total debt, face value", short: "Total debt", kind: "total", d: sub.total_debt }],
          source: "Caesars Q2 2026 10-Q debt table; subtotals calculated from the cited rows"
        }, { height: 200 });
      },
      detail: function (body) {
        body.appendChild(periodTable(T.creditMetrics));
        body.appendChild(el("p", { class: "na-note", text: T.creditMetrics.note }));
        body.appendChild(periodTable(T.balanceSheet));
      }
    },
    business: {
      title: "Business and operating model", model: true,
      headline: "Fertitta Entertainment agreed on {C11} to acquire Caesars for {C210|US$/sh} in cash, a transaction valued at {C212|US$ bn} including assumed debt of {C213|US$ bn}; the new debt has no stated amount [G8].",
      lede: null,
      detail: function (body) {
        operatingModelFull(body);
        body.appendChild(subh("Merger terms"));
        body.appendChild(figKv("Merger terms", ["issuer.merger.acquirer_brand", "issuer.merger.parent", "issuer.merger.parent_guarantor", "issuer.merger.agreement_date",
          "merger_price_per_share_pr", "merger_transaction_value", "merger_assumed_debt", "merger_premium_unaffected", "merger_premium_vwap", "issuer.merger.financing",
          "issuer.merger.financing_condition", "merger_go_shop_end", "merger_initial_end_date", "issuer.merger.caesars_advisors", "issuer.merger.fertitta_advisors"]));
        if (M.primary) {
          var sink = [];
          body.appendChild(subh("Transaction summary and new debt issues"));
          body.appendChild(el("p", {}, itemNodes(I.transactionSummary, sink)));
          body.appendChild(newDebtTable());
          var tn = sourceNote(sink);
          if (tn) body.appendChild(tn);
        }
        body.appendChild(subh("Segments, Q2 2026 against Q2 2025"));
        body.appendChild(periodTable(T.segments));
        body.appendChild(subh("Catalysts and near-term events"));
        var sinkC = [];
        body.appendChild(el("table", { class: "dt" }, [el("caption", { class: "vh", text: "Catalysts" }), el("tbody", {}, I.catalysts.map(function (c) {
          return el("tr", {}, [el("td", {}, itemNodes(c, sinkC))]);
        }))]));
        var cn = sourceNote(sinkC);
        if (cn) body.appendChild(cn);
      }
    },
    delta: {
      title: "Earnings delta", ledeTitle: "Segment change, Q2 2026 against Q2 2025", detailTitle: "Segments table",
      headline: "Q2 2026 against Q2 2025: Regional Adjusted EBITDA rose to {C96|US$ m} from {C97|US$ m} while Las Vegas fell to {C94|US$ m} from {C95|US$ m}; the cash side of the delta is available for six months only [G3].",
      lede: function (host) { draw("dumbbell", host, K.segments); },
      detail: function (body) { body.appendChild(periodTable(T.segments)); }
    },
    quality: {
      title: "Earnings quality", ledeTitle: "Adjusted EBITDA bridge", detailTitle: "EBITDA adjustments",
      headline: "Q2 2026 Adjusted EBITDA of {K66|US$ m} reconciles from a net loss of {C192|US$ m}; the add-backs are transaction costs of {C204|US$ m} and stock-based compensation of {C206|US$ m}, and none is unrealized [G22].",
      lede: function (host) { draw("waterfall", host, K.ebitdaBridge, { height: 230 }); },
      detail: function (body) { body.appendChild(periodTable(T.ebitdaAdjustments)); body.appendChild(el("p", { class: "na-note", text: T.ebitdaAdjustments.note })); }
    },
    fundamentals: {
      title: "Fundamentals, liquidity and cash flow", ledeTitle: "Cash bridge", detailTitle: "Interest path, liquidity and maturities",
      headline: "Cash and revolver capacity of {C177|US$ m} at 30 June 2026 against {C178|US$ m} of debt due in the rest of 2026; H1 2026 free cash flow of {K44|US$ m} after capex of {C45|US$ m}.",
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
      title: "Downside", ledeTitle: "Risk matrix", detailTitle: "Risk register", illusDetail: true,
      headline: "Two events sit in the high zone: the merger's new debt of unstated size [G8] and the Las Vegas trend, where Adjusted EBITDA fell to {C94|US$ m} from {C95|US$ m}.",
      lede: function (host) { draw("riskMatrix", host, K.risk); },
      detail: function (body) {
        body.appendChild(table("Risk register", [th("Event"), th("Description"), th("Probability"), th("Impact"), th("Classification")], K.risk.events.map(function (e) {
          return el("tr", {}, [rowTh(e.key + " " + e.label), el("td", {}, [txt(e.description), e.ref ? UI.chip(e.ref) : null]),
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
        v.appendChild(subh("Scores and valuation", [UI.illus()]));
        v.appendChild(scoresTable());
        body.appendChild(el("p", { class: "na-note", text: K.peerRange.note }));
      }
    },
    legal: {
      title: "Legal and covenants", ledeTitle: "Covenant headroom", detailTitle: "Merger agreement protections and missing documents",
      headline: "No maintenance covenant level is cited [G17], so headroom is not drawn against net leverage of {K56|x}; the merger agreement carries a reverse termination fee of {C226} and an End Date of {C220}.",
      lede: function (host) {
        var row = K.covenant.rows[0];
        if (!row || row.threshold.v === null || row.threshold.v === undefined) {
          /* no level to measure against: a bar for current leverage labelled as a ceiling would be read as the covenant */
          naFigure(host, { id: K.covenant.id, title: K.covenant.title, summary: K.covenant.summary,
            missing: "Needs the maximum net leverage level from the credit agreement; net leverage today is " + noteValue("K56") + ", with nothing to measure it against.",
            refs: ["G17"], source: K.covenant.source });
        } else draw("bullet", host, K.covenant);
      },
      detail: function (body) {
        body.appendChild(figKv("Merger agreement protections", ["issuer.merger.financing_condition", "merger_termination_fee", "merger_termination_fee_reduced",
          "merger_reverse_termination_fee", "merger_initial_end_date", "merger_first_extended_end_date", "merger_second_extended_end_date", "merger_ticking_fee_date", "merger_ticking_fee_per_day"]));
      }
    },
    qa: {
      title: "Evidence QA", ledeTitle: "Evidence counts", detailTitle: "Reconciliations",
      headline: function () {
        return "Every figure carries a citation or a formula; total debt by facility sums to {K60|US$ m} against a stated {C114|US$ m}, and the H1 2026 cash bridge leaves {K67|US$ m} unexplained by the extracted lines [G26].";
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
        var q = hostOf("quality"), fu = hostOf("fundamentals");
        body.appendChild(table("Reconciliations", [th("Check"), th("Stated", "US$ m", true), th("Calculated", "US$ m", true), th("Note")], [
          el("tr", {}, [rowTh("Total debt by facility"), tdD(refDatum("C114")), tdD(refDatum("K60")), el("td", { text: "The facility rows sum to the stated total." })]),
          el("tr", {}, [rowTh("Q2 2026 Adjusted EBITDA bridge"), tdD(fd("recon_adj_ebitda_q2_2026")), tdD(refDatum("K66")), el("td", {}, [txt("Net loss to Adjusted EBITDA reconciles; see "),
            el("a", { href: "#" + slug(q ? q.id : "CP-1") + "-quality", text: "Earnings quality" })])]),
          el("tr", {}, [rowTh("H1 2026 closing cash"), tdD(refDatum("C104")), tdD(fd("cash_bridge_closing_from_lines_h1_2026")),
            el("td", {}, rich("Opening cash plus cash from operations less capex gives the calculated figure; the difference of {K67|US$ m} is financing and other flows the extracted lines do not name. See the ").concat([
              el("a", { href: "#" + (fu ? slug(fu.id) + "-figure" : "snapshot"), text: "cash bridge" }), txt(".")]))])
        ]));
      }
    },
    fit: {
      title: "Portfolio fit", ledeTitle: "Sector weights", detailTitle: "Checks",
      headline: function () { return P.fit.summary; },
      /* the Portfolio Fit view already opens with this summary */
      noHeadline: true,
      synthetic: true,
      lede: function (host) { draw("rangeStrip", host, K.cloSectors); },
      detail: null
    },
    challenge: {
      title: "Committee challenge", ledeTitle: "Challenges", detailTitle: "Responses", illusLede: true,
      headline: function () {
        var qs = QUESTIONS.map(function (q) { return q.charAt(0).toLowerCase() + q.slice(1).replace(/\?$/, ""); });
        return "Committee will ask: " + qs[0] + "; " + qs[1] + "; and " + qs[2] + "?";
      },
      lede: function (host) {
        var sink = [];
        host.appendChild(table("Challenges", [th("Challenge"), th("Rests on")], I.weaknesses.map(function (w) {
          return el("tr", {}, [rowTh(w.label), el("td", {}, itemNodes(w, sink))]);
        })));
        var n = sourceNote(sink);
        if (n) host.appendChild(n);
      },
      detail: function (body) { body.appendChild(el("p", { class: "na-note", text: "Responses to each challenge would come from the run; none exists for this mockup." })); }
    }
  };
  /* a model-written headline: one Model tag on its block, the figures inside it as buttons */
  function headlineNodes(t, m) {
    var str = typeof t.headline === "function" ? t.headline(m) : t.headline;
    var nodes = rich(str);
    if (t.synthetic) nodes.push(el("span", { class: "synth", text: "Synthetic" }));
    return { nodes: nodes, refs: refsIn(str) };
  }

  /* extra sections a module view carries beyond its figure, tables and sources */
  var EXTRAS = {
    financials: function (v, sid, add) {
      add({ key: "capital-structure", title: "Capital structure", meta: ["At " + T.capitalStructure.asOf + "; multiples are cumulative, x LTM Adjusted EBITDA"], flush: true }, function (b) {
        b.appendChild(capitalTable());
        b.appendChild(srcNote("", rich("EBITDA basis: " + T.capitalStructure.ebitda_basis + ". Financing obligations to GLPI and VICI of {C184|US$ m} are shown in the balance sheet, not added to debt.")));
      });
      add({ key: "financials", title: "Financials", meta: [T.financials.unit + "; negatives in parentheses as filed"], flush: true }, function (b) { b.appendChild(periodTable(T.financials)); });
      add({ key: "history", title: "Historical performance", model: true }, function (b) {
        var sink = [];
        b.appendChild(el("p", {}, itemNodes(I.historicalPerformance, sink)));
        draw("columns", figHost(b), K.revenueEbitda, { height: 200 });
        var n = sourceNote(sink);
        if (n) b.appendChild(n);
      });
    },
    rv: function (v, sid, add) {
      add({ key: "credit-view", title: "Credit view: thesis, strengths and weaknesses", illus: true, model: true }, function (b) {
        var sink = [];
        var thesis = itemNodes(I.thesis, sink);
        b.appendChild(annot([el("p", {}, thesis)], sink));
        var sink2 = [];
        var grid = el("div", { class: "swgrid" }, [
          el("div", {}, [el("div", { class: "bar bar--sub", text: "Strengths" }), swRows(I.strengths, sink2)]),
          el("div", {}, [el("div", { class: "bar bar--sub", text: "Weaknesses" }), swRows(I.weaknesses, sink2)])
        ]);
        b.appendChild(grid);
        var n = sourceNote(sink2);
        if (n) b.appendChild(n);
      });
      add({ key: "loan-rv", title: "Loan relative value", meta: ["Index: Bloomberg US Leveraged Loan Index"], flush: true }, function (b) { b.appendChild(loanRv()); });
      add({ key: "hy-rv", title: "High-yield relative value", meta: ["Index: Bloomberg US Corporate High Yield Index; bonds: " + T.trace.title], flush: true }, function (b) { b.appendChild(hyRv()); });
    },
    intake: function (v, sid, add) {
      add({ key: "profile", title: "Company profile", flush: true, open: false }, function (b) { b.appendChild(profileTable()); });
    }
  };

  /* Build one module's analysis. A module whose topic belongs to another view (CP-5 to Evidence, CP-6 to Portfolio
     Fit) renders inside that view as a section with the same content; its own address still works. */
  function buildModule(m, navIdx) {
    var into = foldOf(m);
    var id = modId(m), sid = slug(m.id), t = topicOf(m), topic = t ? TOPICS[t] : null, name = plainName(m);
    var v, root, level, hd;
    gapHref = "#" + sid + "-gaps";
    if (into) {
      v = VIEWS[into]; curView = into; curPre = PRE[into]; subLevel = 4; level = 3;
      root = el("section", { class: "fold", id: id, "aria-labelledby": id + "-h" });
      v.el.appendChild(root);
      hd = el("header", { class: "vhead vhead--fold" }, [el("div", { class: "vhead__top" }, [el("h2", { class: "fold__t", id: id + "-h", text: name }),
        el("span", { class: "vhead__code", title: "RBOT module code", text: m.id })])]);
      root.appendChild(hd);
    } else {
      v = newView(id, { title: name, group: "Analysis", h1: name, cls: "view--module", pre: m.id });
      v.mod = m; v.code = m.id;
      root = v.el; level = 2;
      hd = plainHead(v, null, m.id);
    }
    var facts = el("div", { class: "vfacts" });
    hd.appendChild(facts);
    facts.appendChild(el("div", { class: "vfact" }, [el("p", { class: "vfact__v vfact__q" }, [el("span", { text: "Question: " }), txt(m.question)])]));
    var st = el("p", { class: "vfact__v" }, [txt(m.reason + " ")]);
    (m.refs || []).forEach(function (r) { st.appendChild(chipFor(r)); });
    facts.appendChild(el("div", { class: "vfact" }, [el("span", { class: "vfact__k" }, ["Status ", UI.status(m.status)]), st]));
    var hl = topic && !topic.noHeadline ? headlineNodes(topic, m) : null;
    if (hl) hd.appendChild(el("div", { class: "headline" }, [el("p", { class: "headline__v" }, hl.nodes.concat([txt(" "), modelTag()]))]));
    else if (!topic) hd.appendChild(el("p", { class: "na-note", text: "No headline finding is written for this module." }));
    /* the headline's sources, one disclosure under it; gaps are stated once, under Gaps and limitations */
    var srcRefs = hl ? hl.refs.filter(function (r) { return !D.gaps[r]; }) : [];
    if (srcRefs.length) hd.appendChild(sourcesDisclosure(srcRefs));

    function add(o, build) {
      var body = cb(root, { title: o.title, short: o.short, id: o.key ? sid + "-" + o.key : null, paper: true, level: level, meta: o.meta, illus: o.illus, model: o.model, synth: o.synth,
        flush: o.flush, open: o.open, nav: into ? false : undefined });
      build(body);
    }
    if (topic && topic.lede) add({ key: "figure", title: topic.ledeTitle || "Figures", illus: topic.illusLede }, function (b) { topic.lede(b, m); });
    if (topic && topic.detail) add({ key: "detail", title: topic.detailTitle || "Detailed tables", illus: topic.illusDetail, model: topic.model }, function (b) { topic.detail(b, m); });
    if (t && EXTRAS[t]) EXTRAS[t](v, sid, add);
    /* topics with no module of their own join this one */
    Object.keys(HOST).forEach(function (sub) {
      if (hostOf(sub) !== m || OWNED[sub] || sub === t) return;
      var tp = TOPICS[sub], h2 = headlineNodes(tp);
      add({ key: sub, title: tp.title, model: tp.model, illus: tp.illusLede || tp.illusDetail }, function (b) {
        b.appendChild(el("p", { class: "lede-line" }, h2.nodes));
        var hs = h2.refs.filter(function (r) { return !D.gaps[r]; });
        if (hs.length) b.appendChild(sourcesDisclosure(hs));
        if (tp.lede) tp.lede(figHost(b));
        if (tp.detail) tp.detail(b);
      });
    });
    /* its gaps and limitations, each stated once: every gap the module's status and findings cite */
    var gapRefs = (m.refs || []).filter(function (r) { return D.gaps[r]; });
    function addGaps(r) { if (D.gaps[r] && gapRefs.indexOf(r) < 0) gapRefs.push(r); }
    if (hl) hl.refs.forEach(addGaps);
    Object.keys(HOST).forEach(function (sub) {
      if (hostOf(sub) === m && !OWNED[sub] && sub !== t) refsIn(typeof TOPICS[sub].headline === "function" ? TOPICS[sub].headline() : TOPICS[sub].headline).forEach(addGaps);
    });
    add({ key: "gaps", title: "Gaps and limitations" }, function (b) {
      if (gapRefs.length) b.appendChild(gapTable(gapRefs, "Gaps raised against " + name));
      else b.appendChild(el("p", { class: "na-note", text: "No gap is raised against this module. The run-wide limitations are on the Limitations view." }));
    });
    gapHref = null;
    if (into) return;
    /* previous and next */
    var i = NAV_MODS.indexOf(m), prevM = NAV_MODS[i - 1], nextM = NAV_MODS[i + 1];
    var prev = prevM ? { href: "#" + modId(prevM), k: "Previous module", t: plainName(prevM) } : { href: "#snapshot", k: "Back to", t: "Snapshot" };
    var next = nextM ? { href: "#" + modId(nextM), k: "Next module", t: plainName(nextM) } : { href: "#model", k: "Next view", t: "Model" };
    v.el.appendChild(el("nav", { class: "pager", "aria-label": "Previous and next module" }, [
      el("a", { class: "pager__a pager__a--prev", href: prev.href }, [el("span", { class: "pager__k", text: prev.k }), el("span", { class: "pager__t", text: prev.t })]),
      el("a", { class: "pager__a pager__a--next", href: next.href }, [el("span", { class: "pager__k", text: next.k }), el("span", { class: "pager__t", text: next.t })])
    ]));
  }
  function sourcesDisclosure(refs) {
    return el("details", { class: "srcs srcs--head" }, [el("summary", { text: "Sources (" + refs.length + ")" }), el("div", { class: "src-notes src-notes--inline" }, [notes(refs)])]);
  }
  function buildFolded(viewId) {
    MODS.forEach(function (m) { if (foldOf(m) === viewId) buildModule(m); });
  }

  /* ================================================================ 3. MODEL */
  function buildModel() {
    var v = newView("model", { title: "Model", pre: "M" });
    plainHead(v, ["Values-only twin of model.xlsx. Select any figure for its source, locator and excerpt, or its formula."]);
    var fin = T.financials;
    var earningsRows = function (r) { return fin.rows.indexOf(r) <= 5; };
    var cashRows = function (r) { return fin.rows.indexOf(r) >= 6; };
    var bands = [
      { id: "model-earnings", t: "Earnings", lede: "LTM net revenues {K1|US$ m} and Adjusted EBITDA {K2|US$ m}, a margin of {K47|%}; FY2023 Adjusted EBITDA was {C74|US$ m}.",
        fig: function (h) { draw("columns", h, K.revenueEbitda, { height: 190 }); }, body: function (b) { b.appendChild(periodTable(fin, earningsRows, "Earnings")); } },
      { id: "model-ebitda-bridge", t: "Adjusted EBITDA bridge", lede: "A Q2 2026 net loss of {C192|US$ m} becomes Adjusted EBITDA of {K66|US$ m} once interest, depreciation and amortisation are added back, with transaction costs of {C204|US$ m} and stock-based compensation of {C206|US$ m}; SSIM equals Structuring [G22].",
        fig: function (h) { draw("waterfall", h, K.ebitdaBridge, { height: 230 }); }, body: function (b) { b.appendChild(periodTable(T.ebitdaAdjustments)); b.appendChild(el("p", { class: "na-note", text: T.ebitdaAdjustments.note })); } },
      { id: "model-cash-flow", t: "Cash flow waterfall", lede: "LTM cash from operations {K4|US$ m} less capex {K3|US$ m} leaves free cash flow of {K50|US$ m}; lease cash interest of {K9|US$ m} runs through rent.",
        fig: function (h) { draw("waterfall", h, K.cashBridge, { height: 220 }); }, body: function (b) { b.appendChild(periodTable(fin, cashRows, "Cash flow")); } },
      { id: "model-debt-stack", t: "Debt stack by rank", lede: "Senior secured {K57|US$ m}, unsecured {K58|US$ m} and other {K59|US$ m}: total debt {C114|US$ m} at face; financing obligations of {C184|US$ m} are shown apart from debt.",
        fig: function (h) { TOPICS.financials.lede(h); }, body: function (b) { b.appendChild(debtStack()); } },
      { id: "model-credit-metrics", t: "Credit metrics, liquidity and maturities", lede: "Total leverage {K55|x}, net {K56|x} and senior {K61|x}; interest cover {K51|x}, or {K52|x} on debt cash interest alone. Accessible liquidity is {C177|US$ m}; the maturity wall shows face value at final maturity, while the 10-Q table, with amortisation, has {C182|US$ m} in 2030.",
        fig: function (h) {
          var a = el("div", { class: "figpair" }), b = el("div", { class: "figpair" });
          h.appendChild(a); h.appendChild(b);
          draw("lineStrip", figHost(a), K.leverage, { height: 170 }); draw("lineStrip", figHost(a), K.coverage, { height: 170 });
          draw("lineStrip", figHost(b), K.liquidity, { height: 170 }); draw("stackedColumns", figHost(b), K.maturityWall, { height: 170 });
        },
        body: function (b) {
          b.appendChild(periodTable(T.creditMetrics)); b.appendChild(periodTable(T.balanceSheet));
          var two = el("div", { class: "figpair" });
          b.appendChild(two);
          two.appendChild(rowsTable(T.liquidity)); two.appendChild(rowsTable(T.maturities));
        } }
    ];
    bands.forEach(function (bd, i) {
      var body = cb(v.el, { title: bd.t, short: bd.t.replace(/, liquidity and maturities$/, ""), id: bd.id, paper: true, open: i < 2 });
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
  function synthD(text, ref) { return { v: text, prov: "synthetic", ref: ref }; }
  function buildFit() {
    var fit = P.fit;
    var v = newView("portfolio-fit", { title: "Portfolio Fit", h1: "Portfolio Fit: " + P.name, pre: "PF" });
    plainHead(v, ["Portfolio as of " + P.asOf + ". The mandate, holdings and limits are synthetic Test CLO I files."]);
    var body = cb(v.el, { title: "Fit checks", id: "portfolio-fit-checks", paper: true, synth: true, illus: true, model: true });
    var grid = el("div", { class: "pf-summary" });
    body.appendChild(grid);
    var left = el("div"), right = el("div");
    grid.appendChild(left); grid.appendChild(right);
    left.appendChild(el("div", { class: "pf-verdict" }, [subh("Portfolio Fit"), UI.status(fit.overall.v)]));
    left.appendChild(el("p", {}, [txt(fit.summary)]));
    left.appendChild(table("Fit checks", [th("Constraint"), th("Limit"), th("Current", null, true), th("Headroom", null, true), th("Result")], fit.checks.map(function (c) {
      return el("tr", {}, [rowTh(c.constraint), nowrap(el("td", { text: c.limit })), tdD(synthD(c.current, c.ref)),
        el("td", { class: "num", text: c.headroom }), el("td", {}, [UI.status(c.result), c.note ? el("div", { class: "gap__reason", text: c.note }) : null])]);
    })));
    draw("bullet", right, K.cloLimits);
    var inst = cb(v.el, { title: "Fit by instrument", id: "portfolio-fit-instrument", paper: true, synth: true, illus: true });
    inst.appendChild(table("Fit by instrument", [th("Instrument"), th("Fit"), th("Note")], fit.byInstrument.map(function (b) {
      return el("tr", {}, [rowTh(b.instrument), el("td", {}, [UI.status(b.fit)]), el("td", { text: b.note || "" })]);
    })));
    var det = cb(v.el, { title: "Test CLO I: constraints, summary, mandate and sectors", id: "portfolio-fit-detail", paper: true, synth: true, open: false });
    det.appendChild(subh("Constraint schedule"));
    det.appendChild(table("Constraints", [th("ID"), th("Category"), th("Parameter"), th("Limit"), th("Type"), th("Current", null, true), th("Headroom", null, true), th("Status"), th("Source")],
      P.constraints.map(function (c) {
        return el("tr", {}, [rowTh(c.id), el("td", { text: c.category }), el("td", { text: c.parameter }), el("td", { text: c.limit }),
          el("td", { text: c.breachType }), tdD(synthD(c.current, c.ref)), el("td", { class: "num", text: c.headroom }), el("td", {}, [UI.status(c.status)]), el("td", { text: c.sourceDocument })]);
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
    var sh = subh("Sector weights");
    sh.style.marginTop = "var(--s-4)";
    det.appendChild(sh);
    det.appendChild(table("Sectors", [th("Sector"), th("% NAV", null, true), th("Issuers", null, true), th("Limit"), th("Headroom", null, true), th("Status")],
      P.sectors.map(function (x) {
        return el("tr", {}, [rowTh(x.sector), el("td", { class: "num", text: x.pct }), el("td", { class: "num", text: x.issuers }), el("td", { text: x.limit }),
          el("td", { class: "num", text: x.headroom }), el("td", {}, [UI.status(x.status)])]);
      })));
    buildFolded("portfolio-fit");
  }

  /* ================================================================ 5. EVIDENCE */
  function buildEvidence() {
    var c = D.counts;
    var v = newView("evidence", { title: "Evidence", pre: "E" });
    plainHead(v, ["Every citation with its verbatim excerpt, every calculation with its formula and inputs: " + c.cited + " cited, " + c.calculated + " calculated, " + c.gaps + " gaps, " + c.synthetic_sources + " synthetic."]);
    buildFolded("evidence");
    cb(v.el, { title: "Documents admitted", id: "evidence-documents", paper: true }).appendChild(docTable());
    var cites = Object.keys(D.citations).filter(function (k) { return !D.citations[k].synthetic; });
    var synth = Object.keys(D.citations).filter(function (k) { return D.citations[k].synthetic; });
    function citeRows(ids) {
      return ids.map(function (id) {
        var x = D.citations[id];
        return el("tr", { id: "cite-" + id }, [el("th", { scope: "row" }, [UI.chip(id)]), el("td", { text: x.label }), el("td", { class: "num", text: x.value }),
          el("td", { text: (x.period || "").replace(/^as of /, "") }), el("td", { text: x.file }), el("td", { text: x.locator || "" }), el("td", { class: "ex", text: x.excerpt })]);
      });
    }
    var citeCols = function () { return [th("ID"), th("Figure"), th("Value as served", null, true), th("Period"), th("File"), th("Locator"), th("Excerpt")]; };
    [["evidence-citations", "Citations (" + cites.length + ")", function () { return tall(table("Citations", citeCols(), citeRows(cites), "evid")); }],
     ["evidence-calcs", "Calculations (" + Object.keys(D.calcs).length + ")", function () {
       return tall(table("Calculations", [th("ID"), th("Figure"), th("Period"), th("Value", null, true), th("Formula"), th("Inputs")], Object.keys(D.calcs).map(function (id) {
         var k = D.calcs[id], ins = el("td");
         (k.inputs || []).forEach(function (r) { ins.appendChild(UI.chip(r)); });
         return el("tr", { id: "calc-" + id }, [el("th", { scope: "row" }, [UI.chip(id)]), el("td", { text: k.label }), el("td", { text: k.period || "" }), el("td", { class: "num", text: k.value }),
           el("td", {}, [el("code", { text: k.formula })]), ins]);
       }), "evid"));
     }],
     ["evidence-synthetic", "Synthetic portfolio rows (" + synth.length + ")", function () { return tall(table("Synthetic rows", citeCols(), citeRows(synth), "evid")); }]
    ].forEach(function (x) {
      cb(v.el, { title: x[1], id: x[0], paper: true, open: false, flush: true, search: false }).appendChild(x[2]());
    });
  }
  function tall(node) { node.classList.add("tall-scroll"); return node; }

  /* ================================================================ 6. LIMITATIONS */
  function buildLimitations() {
    var L = D.limitations;
    var nModel = L.filter(function (l) { return /^Model limitation/.test(l.scope); }).length;
    var v = newView("limitations", { title: "Limitations", pre: "L" });
    plainHead(v, ["Stated before the run and carried into the Report. " + L.length + " were known at Approval: " + (L.length - nModel) + " inputs missing from the Source Pack and " + nModel + " limits of the Model itself."]);
    var model = L.filter(function (l) { return /^Model limitation/.test(l.scope); });
    function limRows(list, prefix) {
      return list.map(function (l) {
        return el("tr", { id: prefix ? prefix + l.ref : null }, [el("th", { scope: "row" }, [UI.chip(l.ref)]), el("td", { text: human(l.field) }), el("td", { text: l.text }), el("td", { text: /^Model limitation/.test(l.scope) ? "Model" : l.scope.replace(/^Source Pack gap$/, "Source Pack") }), el("td", { text: originText(l.origin) })]);
      });
    }
    var cols = function () { return [th("Gap"), th("Missing item"), th("Limitation"), th("Scope"), th("Origin")]; };
    var b1 = cb(v.el, { title: "Model limitations", id: "limitations-known", paper: true });
    if (model.length) {
      b1.appendChild(el("p", { text: "These limit the Model itself:" }));
      b1.appendChild(table("Model limitations", cols(), limRows(model)));
    } else b1.appendChild(el("p", { class: "na-note", text: "No limitation of the Model itself is recorded." }));
    cb(v.el, { title: "All " + L.length + " limitations known at Approval", id: "limitations-all", paper: true, open: false, flush: true })
      .appendChild(table("Limitations known at Approval", cols(), limRows(L, "limit-")));
    var b2 = cb(v.el, { title: "Unforeseen", id: "limitations-unforeseen", paper: true });
    var U = D.unforeseen || [];
    if (U.length) b2.appendChild(table("Unforeseen limitations", cols(), limRows(U)));
    else b2.appendChild(el("p", { text: "None recorded. No RBOT run exists, so nothing arose after Approval." }));
  }

  /* ================================================================ navigation pane */
  /* the pane holds the Report's 11 destinations and nothing else; each view's own sections are a contents line in the paper */
  function buildNav() {
    var nav = document.getElementById("nav");
    var ul = el("ul", { class: "nav__list" });
    function link(id, label, code, status) {
      var a = el("a", { class: "nav__a", href: "#" + id, "data-view": id }, [
        el("span", { class: "nav__t", text: label }),
        code ? el("span", { class: "nav__code", title: "RBOT module code", text: code }) : null,
        status ? el("span", { class: "on-navy nav__st" }, [UI.status(status)]) : null,
        status ? el("span", { class: "nav__stw", "aria-hidden": "true", text: UI.statusLabel(status) }) : null
      ]);
      VIEWS[id].nav = a;
      return el("li", {}, [a]);
    }
    ul.appendChild(link("snapshot", "Snapshot"));
    var tally = {};
    NAV_MODS.forEach(function (m) { tally[m.status] = (tally[m.status] || 0) + 1; });
    var grp = el("li", { class: "nav__grp" }, [
      el("span", { class: "nav__gt", id: "nav-analysis-h", text: "Analysis" }),
      el("span", { class: "nav__gm", text: NAV_MODS.length + " modules: " + Object.keys(tally).map(function (k) { return tally[k] + " " + UI.statusLabel(k).toLowerCase(); }).join(", ") }),
      el("ul", { "aria-labelledby": "nav-analysis-h" }, NAV_MODS.map(function (m) { return link(modId(m), plainName(m), m.id, m.status); }))
    ]);
    ul.appendChild(grp);
    ["model", "portfolio-fit", "evidence", "limitations"].forEach(function (id) { ul.appendChild(link(id, VIEWS[id].title)); });
    nav.appendChild(ul);
    document.getElementById("pane-issuer").textContent = M.issuer.replace(/, Inc\.$/, "") + " (" + M.ticker + ")";
    document.getElementById("pane-meta").textContent = M.pathway + " · " + M.reportingPeriod + " · Analysis " + fmtDate(parseDate(M.analysisDate), "table");
  }
  /* a view's contents line: its sections as links under the H1; the one in view carries aria-current="location" */
  var spy = { items: [] };
  function buildToc(v) {
    var items = [];
    Array.prototype.forEach.call(v.el.querySelectorAll("details.cb[id], section.fold[id]"), function (d) {
      if (d.getAttribute("data-nav") === "skip") return;
      if (d.parentElement && d.parentElement.closest("details.cb")) return;
      var h = d.querySelector(".cb__t, .fold__t");
      if (h) items.push({ el: d, label: d.getAttribute("data-short") || h.textContent });
    });
    v.toc = items;
    if (items.length < 2) return;
    var ul = el("ul", { class: "toc__list" }, items.map(function (it) {
      it.a = el("a", { href: "#" + it.el.id, text: it.label });
      return el("li", {}, [it.a]);
    }));
    var nav = el("nav", { class: "toc", "aria-label": "Sections of " + v.title }, [el("span", { class: "toc__k", text: "On this page" }), ul]);
    if (v.tocSlot) v.tocSlot.appendChild(nav);
    else {
      var hd = v.el.querySelector(":scope > header"), anchor = hd && (hd.querySelector(".vhead__lede") || hd.querySelector(".vhead__top"));
      if (anchor) anchor.insertAdjacentElement("afterend", nav);
    }
  }
  var spyTimer = 0;
  function updateSpy() {
    if (spyTimer) return;
    spyTimer = setTimeout(function () {
      spyTimer = 0;
      var cur = null, line = 140;
      spy.items.forEach(function (it) { if (it.a && it.el.getBoundingClientRect().top <= line) cur = it; });
      spy.items.forEach(function (it) {
        if (!it.a) return;
        if (it === cur) { if (it.a.getAttribute("aria-current") !== "location") it.a.setAttribute("aria-current", "location"); }
        else it.a.removeAttribute("aria-current");
      });
    }, 50);
  }

  /* how to read a figure: a popover in the view header (the pane keeps only the Report's destinations) */
  var keyPop = null, keyBtn = null;
  function buildKeyBody(host) {
    function row(mark, text) { return el("li", {}, [el("span", { class: "key__m" }, [mark]), el("span", { text: text })]); }
    function sw(cls) { return el("i", { class: "prov-swatch prov-swatch--" + cls, "aria-hidden": "true" }); }
    host.appendChild(el("ul", { class: "key__list" }, [
      row(sw("cited"), "Cited figure: select it for file, line and excerpt"),
      row(sw("calculated"), "Calculated figure: select it for the formula and its inputs"),
      row(sw("synthetic"), "Synthetic: a Test CLO I file row"),
      row(el("span", { class: "gapref", "aria-hidden": "true", text: "G8" }), "n/a: missing from the sources, with its reason"),
      row(el("span", { class: "cite key__chip", "aria-hidden": "true", text: "C12" }), "Source note: citation, calculation or gap id"),
      row(el("span", { class: "tag-model", text: "Model" }), "Written by the model from cited figures; dotted rule on the block"),
      row(el("span", { class: "illus", text: "Illustrative" }), "A judgement; no RBOT run exists"),
      row(el("span", { class: "synth", text: "Synthetic" }), "Test CLO I data")
    ]));
    host.appendChild(el("p", { class: "key__h", text: "House scales" }));
    host.appendChild(el("p", { class: "key__p" }, [UI.scale({ kind: "rec", pos: 2, word: "Modest OW", label: "Example" }),
      txt(" Position 1 is the strongest (Strong OW, Strong, V1) and 5 the weakest; the meter marks the position. The word carries the meaning; colour does not.")]));
    host.appendChild(el("p", { class: "key__h", text: "Module status in the pane" }));
    host.appendChild(el("ul", { class: "key__list key__list--status" }, ["Pass", "Restricted", "Blocked"].map(function (w) {
      return el("li", {}, [el("span", { class: "key__m key__m--navy" }, [el("span", { class: "on-navy nav__st" }, [UI.status(w)])]),
        el("span", { text: UI.statusLabel(w) + ": " + (w === "Pass" ? "checks reconcile" : w === "Restricted" ? "some inputs are missing, reason stated" : "cannot run") })]);
    })));
    host.appendChild(el("p", { class: "key__h", text: "Keys" }));
    host.appendChild(el("p", { class: "key__p" }, [el("kbd", { text: "/" }), txt(" searches the Report. Arrow keys move between figures in a table, a list or a chart; "), el("kbd", { text: "Esc" }), txt(" closes this and any source.")]));
  }
  function keyButton() {
    var b = el("button", { type: "button", class: "btn btn--quiet vkey", "aria-haspopup": "dialog", "aria-expanded": "false", text: "How to read a figure" });
    b.addEventListener("click", function () { if (keyBtn === b && keyPop && !keyPop.hidden) closeKey(true); else openKey(b); });
    return b;
  }
  function openKey(b) {
    if (!keyPop) {
      keyPop = el("div", { class: "keypop", role: "dialog", "aria-label": "How to read a figure", tabindex: "-1", hidden: true });
      buildKeyBody(keyPop);
      document.body.appendChild(keyPop);
    }
    UI.close(false);
    if (keyBtn) keyBtn.setAttribute("aria-expanded", "false");
    keyBtn = b;
    b.setAttribute("aria-expanded", "true");
    keyPop.hidden = false;
    var r = b.getBoundingClientRect(), w = keyPop.offsetWidth;
    keyPop.style.left = Math.max(8, Math.min(window.scrollX + r.right - w, window.scrollX + document.documentElement.clientWidth - w - 8)) + "px";
    keyPop.style.top = (window.scrollY + r.bottom + 6) + "px";
    keyPop.focus({ preventScroll: true });
  }
  function closeKey(restore) {
    if (!keyPop || keyPop.hidden) return;
    keyPop.hidden = true;
    if (keyBtn) { keyBtn.setAttribute("aria-expanded", "false"); if (restore) keyBtn.focus(); }
  }

  /* ================================================================ search */
  var SEARCH = [];
  function plain(s) { return String(s).replace(/\s+/g, " ").trim(); }
  function indexSearch() {
    var seenFig = {};
    ORDER.forEach(function (id) {
      var v = VIEWS[id];
      var secs = v.el.querySelectorAll("details.cb[id], section.fold[id]");
      Array.prototype.forEach.call(secs, function (d) {
        if (d.getAttribute("data-search") === "skip") return;
        if (d.parentElement && d.parentElement.closest("details.cb")) return;
        var h = d.querySelector(".cb__t, .fold__t");
        SEARCH.push({ kind: "Section", view: v.title, title: h ? h.textContent : d.id, target: d.id, text: plain(d.textContent), tl: "" });
      });
      Array.prototype.forEach.call(v.el.querySelectorAll("figure.chart[id]"), function (f) {
        var n = f.querySelector(".chart__num"), t = f.querySelector(".chart__title"), s = f.querySelector(".chart__summary");
        /* a figure drawn in two views is listed once, in the view that numbered it first */
        var key = n ? n.textContent : f.id;
        if (seenFig[key]) return;
        seenFig[key] = true;
        SEARCH.push({ kind: "Figure", view: v.title, title: (n ? n.textContent + " " : "") + (t ? t.textContent : ""), target: f.id, text: plain((t ? t.textContent : "") + " " + (s ? s.textContent : "")) });
      });
    });
    Object.keys(D.citations).forEach(function (id) {
      var c = D.citations[id];
      SEARCH.push({ kind: c.synthetic ? "Synthetic row" : "Citation", view: "Evidence", title: id + " " + c.label, target: "cite-" + id,
        text: plain([id, c.label, c.value, c.period, c.file, c.locator, c.excerpt].join(" ")) });
    });
    Object.keys(D.calcs).forEach(function (id) {
      var k = D.calcs[id];
      SEARCH.push({ kind: "Calculation", view: "Evidence", title: id + " " + k.label, target: "calc-" + id, text: plain([id, k.label, k.value, k.period, k.formula].join(" ")) });
    });
    Object.keys(D.gaps).forEach(function (id) {
      var g = D.gaps[id];
      SEARCH.push({ kind: "Gap", view: "Limitations", title: id + " " + human(g.field), target: "limit-" + id, text: plain([id, human(g.field), g.reason].join(" ")) });
    });
    SEARCH.forEach(function (e) { e.low = e.text.toLowerCase(); e.tl = e.title.toLowerCase(); });
  }
  function runSearch(q) {
    var words = q.toLowerCase().split(/\s+/).filter(Boolean);
    if (!words.length || q.length < 2) return [];
    var hits = [];
    SEARCH.forEach(function (e) {
      if (!words.every(function (w) { return e.low.indexOf(w) >= 0; })) return;
      var score = (words.every(function (w) { return e.tl.indexOf(w) >= 0; }) ? 4 : 0) + (e.kind === "Figure" ? 2 : e.kind === "Section" ? 1 : 0);
      hits.push({ e: e, score: score });
    });
    hits.sort(function (a, b) { return b.score - a.score; });
    return hits;
  }
  function snippet(e, words) {
    var low = e.low, at = -1;
    for (var i = 0; i < words.length && at < 0; i++) at = low.indexOf(words[i]);
    var from = Math.max(0, at - 40), s = e.text.slice(from, from + 120);
    return (from > 0 ? "… " : "") + s + (from + 120 < e.text.length ? " …" : "");
  }
  function markWords(node, text, words) {
    var re = new RegExp("(" + words.map(function (w) { return w.replace(/[.*+?^${}()|[\]\\]/g, "\\$&"); }).join("|") + ")", "ig");
    text.split(re).forEach(function (part, i) { node.appendChild(i % 2 ? el("mark", { text: part }) : txt(part)); });
  }
  function buildSearch() {
    var input = document.getElementById("pane-search"), out = document.getElementById("pane-results"), status = document.getElementById("pane-search-status");
    function render() {
      var q = input.value.trim();
      while (out.firstChild) out.removeChild(out.firstChild);
      if (q.length < 2) { status.textContent = ""; status.hidden = true; out.hidden = true; return; }
      var words = q.toLowerCase().split(/\s+/).filter(Boolean), hits = runSearch(q);
      out.hidden = false;
      status.hidden = false;
      status.textContent = hits.length ? hits.length + (hits.length === 1 ? " result" : " results") : "No results";
      if (!hits.length) { out.appendChild(el("li", { class: "search__none", text: "Nothing in the Report matches “" + q + "”. Try a figure, a module name or a source id such as C12." })); return; }
      hits.forEach(function (h) {
        var a = el("a", { class: "search__a", href: "#" + h.e.target }, [
          el("span", { class: "search__k", text: h.e.kind + " · " + h.e.view }),
          el("span", { class: "search__t", text: h.e.title }),
          el("span", { class: "search__s" }, [])
        ]);
        markWords(a.lastChild, snippet(h.e, words), words);
        out.appendChild(el("li", {}, [a]));
      });
    }
    input.addEventListener("input", render);
    input.addEventListener("keydown", function (e) {
      if (e.key === "ArrowDown") { var a = out.querySelector("a"); if (a) { e.preventDefault(); a.focus(); } }
      if (e.key === "Escape") { input.value = ""; render(); }
    });
    out.addEventListener("keydown", function (e) {
      var links = Array.prototype.slice.call(out.querySelectorAll("a")), i = links.indexOf(document.activeElement);
      if (e.key === "ArrowDown" && i < links.length - 1) { e.preventDefault(); links[i + 1].focus(); }
      if (e.key === "ArrowUp") { e.preventDefault(); (i > 0 ? links[i - 1] : input).focus(); }
      if (e.key === "Escape") { input.focus(); }
    });
    out.addEventListener("click", function (e) { if (e.target.closest("a")) { input.value = ""; render(); } });
    document.addEventListener("keydown", function (e) {
      if (e.key === "/" && !/^(INPUT|TEXTAREA|SELECT)$/.test(document.activeElement.tagName) && !e.metaKey && !e.ctrlKey) {
        e.preventDefault();
        sheetOpen(true);
        input.focus();
      }
    });
  }

  /* ================================================================ router */
  var ALIASES = { "analysis": null, "paper": "snapshot" };
  var activeId = null, traversal = false, scrolls = {};
  var menu = document.getElementById("pane-menu"), sheet = document.getElementById("pane-sheet");
  function sheetOpen(open) {
    menu.setAttribute("aria-expanded", String(open));
    document.getElementById("pane").classList.toggle("is-open", open);
  }
  function viewTitle(v) { return v.title; }
  function hashKey() { return location.hash || "#snapshot"; }
  function show(v, user) {
    if (activeId === v.id) return false;
    if (activeId) { VIEWS[activeId].el.hidden = true; if (VIEWS[activeId].nav) VIEWS[activeId].nav.removeAttribute("aria-current"); }
    activeId = v.id;
    v.el.hidden = false;
    if (v.nav) { v.nav.setAttribute("aria-current", "page"); }
    document.title = viewTitle(v) + " · Credit Snapshot: " + M.issuer + " (" + M.ticker + "), RBOT Report";
    document.getElementById("pane-where").textContent = viewTitle(v);
    document.getElementById("route-live").textContent = viewTitle(v);
    window.scrollTo(0, 0);
    if (user) v.h1.focus({ preventScroll: true });
    closeKey(false);
    charts.forEach(function (c) { c.redraw(); });
    spy = { items: v.toc || [] };
    updateSpy();
    if (v.nav && v.nav.scrollIntoView) { var r = v.nav.getBoundingClientRect(); var pr = document.getElementById("pane-sheet").getBoundingClientRect(); if (r.top < pr.top || r.bottom > pr.bottom) v.nav.scrollIntoView({ block: "nearest" }); }
    return true;
  }
  /* open every closed section around the target, then bring it into view */
  function reveal(t, focus) {
    for (var p = t; p; p = p.parentElement) if (p.tagName === "DETAILS") p.open = true;
    if (t.tagName === "DETAILS") t.open = true;
    requestAnimationFrame(function () {
      t.scrollIntoView({ block: "start" });
      updateSpy();
      if (focus) {
        /* focus lands on the hit, so the screen reader and the viewport agree */
        var f = t.tagName === "DETAILS" ? t.querySelector(":scope > summary") : t;
        if (f && !/^(A|BUTTON|SUMMARY|INPUT)$/.test(f.tagName) && !f.hasAttribute("tabindex")) f.setAttribute("tabindex", "-1");
        if (f) f.focus({ preventScroll: true });
      }
    });
  }
  function route(user) {
    var id = decodeURIComponent(location.hash.replace(/^#/, ""));
    var back = traversal; traversal = false;
    if (id === "main") {   /* the skip link: stay on the current view and land on its heading */
      var cur = VIEWS[activeId || "snapshot"];
      if (!activeId) show(cur, false);
      history.replaceState(null, "", "#" + cur.id);
      cur.h1.focus();
      return;
    }
    var target = null, v = VIEWS[id];
    if (!v && id in ALIASES) v = VIEWS[ALIASES[id] || modId(NAV_MODS[0])];
    if (!v && id) {
      target = document.getElementById(id);
      var owner = target && target.closest ? target.closest(".view") : null;
      v = owner ? VIEWS[owner.getAttribute("data-view")] : null;
    }
    if (!v) v = VIEWS.snapshot;
    var changed = show(v, user && !target);
    if (back && scrolls[hashKey()] != null) { var y = scrolls[hashKey()]; requestAnimationFrame(function () { window.scrollTo(0, y); updateSpy(); }); }
    else if (target) reveal(target, user);
    else if (!changed) window.scrollTo(0, 0);
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
  /* view numbers follow the pane, so a figure's number says where it lives ("Fig. 3.2" is the second figure of view 3) */
  buildSnapshot();
  NAV_MODS.forEach(buildModule);
  buildModel();
  buildFit();
  buildEvidence();
  buildLimitations();
  main.appendChild(el("footer", { class: "foot" }, [txt("Design mockup of an RBOT Report. Caesars figures are taken from its public filings, TRACE pages and peer releases with file and line citations; every score, recommendation, valuation and thesis line is illustrative and is not a view on Caesars. Test CLO I is a synthetic portfolio.")]));
  ORDER.forEach(function (id) { buildToc(VIEWS[id]); });
  buildNav();
  indexSearch();
  buildSearch();
  tidyDates(main);
  UI.init(document);
  UI.roving(main);

  menu.addEventListener("click", function () { sheetOpen(menu.getAttribute("aria-expanded") !== "true"); });
  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape" && keyPop && !keyPop.hidden) { closeKey(true); return; }
    if (e.key === "Escape" && menu.getAttribute("aria-expanded") === "true") { sheetOpen(false); menu.focus(); }
  });
  document.addEventListener("click", function (e) {
    if (menu.getAttribute("aria-expanded") === "true" && !e.target.closest("#pane")) sheetOpen(false);
    if (keyPop && !keyPop.hidden && !e.target.closest(".keypop, .vkey")) closeKey(false);
    /* remember where the reader was before an in-page jump, so Back returns there */
    var a = e.target.closest ? e.target.closest('a[href^="#"]') : null;
    if (a && !e.defaultPrevented) scrolls[hashKey()] = window.scrollY;
  }, true);
  sheet.addEventListener("click", function (e) { if (e.target.closest("a")) sheetOpen(false); });
  var skip = document.querySelector(".skip");
  if (skip) skip.addEventListener("click", function (e) { e.preventDefault(); var cur = VIEWS[activeId || "snapshot"]; window.scrollTo(0, 0); cur.h1.focus(); });
  if ("scrollRestoration" in history) history.scrollRestoration = "manual";
  window.addEventListener("popstate", function () { traversal = true; });
  window.addEventListener("hashchange", function () { route(true); });
  window.addEventListener("scroll", updateSpy, { passive: true });
  document.addEventListener("toggle", updateSpy, true);
  route(false);

  document.documentElement.setAttribute("data-ready", "1");
  function measure() { document.documentElement.setAttribute("data-height", String(document.documentElement.scrollHeight)); }
  measure();
  if (document.fonts && document.fonts.ready) document.fonts.ready.then(function () { setTimeout(measure, 300); });
})();
