/* RBOT Report — vanilla SVG chart kit and small UI layer (no libraries, no innerHTML).
   RBOTCharts.<kind>(element, spec) draws a figure into element and returns
   { redraw(), destroy() }. RBOTUI wires citation popovers, gap reasons and tabs.
   Spec fields and the Datum shape are documented in README.md. */
(function () {
  "use strict";

  var SVGNS = "http://www.w3.org/2000/svg";
  var fmtHook = null;
  var uid = 0;

  /* ------------------------------------------------------------ DOM helpers */
  function set(node, attrs) {
    if (!attrs) return node;
    Object.keys(attrs).forEach(function (k) {
      var v = attrs[k];
      if (v === null || v === undefined || v === false) return;
      if (k === "text") node.textContent = String(v);
      else if (k.slice(0, 2) === "on" && typeof v === "function") node.addEventListener(k.slice(2), v);
      else node.setAttribute(k, v === true ? "" : String(v));
    });
    return node;
  }
  function add(parent, kids) {
    (Array.isArray(kids) ? kids : [kids]).forEach(function (k) {
      if (k === null || k === undefined || k === false) return;
      parent.appendChild(typeof k === "string" ? document.createTextNode(k) : k);
    });
    return parent;
  }
  function h(tag, attrs, kids) { return add(set(document.createElement(tag), attrs), kids || []); }
  function s(tag, attrs, kids) { return add(set(document.createElementNS(SVGNS, tag), attrs), kids || []); }

  /* ------------------------------------------------------------ numbers (floats only place marks) */
  function parseNum(v) {
    if (v === null || v === undefined) return NaN;
    if (typeof v === "number") return v;
    var t = String(v).trim();
    var neg = false;
    if (/^\(.*\)$/.test(t)) { neg = true; t = t.slice(1, -1); }
    t = t.replace(/^[−\-]/, function () { neg = !neg; return ""; });
    t = t.replace(/[,\s$%x]|bps|bp|US|m$|bn$/gi, "");
    if (!/^\d*\.?\d+$/.test(t)) return NaN;
    var n = parseFloat(t);
    return neg ? -n : n;
  }
  function decimals(v) {
    var m = String(v).match(/\.(\d+)/);
    return m ? m[1].length : 0;
  }
  function fmtExact(n, d, parens) {
    var neg = n < 0;
    var abs = Math.abs(n).toFixed(d);
    var parts = abs.split(".");
    parts[0] = parts[0].replace(/\B(?=(\d{3})+(?!\d))/g, ",");
    var out = parts.join(".");
    return neg ? (parens === false ? "-" + out : "(" + out + ")") : out;
  }
  /* Exact sum of decimal strings: scaled integers, printed with the inputs' decimals. */
  function sumExact(values) {
    var d = 0;
    values.forEach(function (v) { d = Math.max(d, decimals(v)); });
    var f = Math.pow(10, d);
    var total = 0;
    values.forEach(function (v) { total += Math.round(parseNum(v) * f); });
    return fmtExact(total / f, d);
  }
  function isGap(d) { return !d || d.v === null || d.v === undefined || isNaN(parseNum(d.v)); } /* numeric: charts */
  function isMissing(d) { return !d || d.v === null || d.v === undefined; } /* textual: tables and prose */
  function withUnit(v, unit) {
    var f = fmtHook ? fmtHook({ v: v }, unit, "chart") : null;
    if (f !== null && f !== undefined) return f;
    if (!unit) return String(v);
    if (unit === "x" || unit === "%" || unit === "pp") return String(v) + unit;
    return String(v) + " " + unit;
  }
  function provWord(d) {
    if (!d) return "";
    var w;
    switch (d.prov) {
      case "cited": w = "cited" + (d.ref ? " " + d.ref : ""); break;
      case "calculated": w = "calculated" + (d.ref ? " " + d.ref : ""); break;
      case "model": w = "model-authored"; break;
      case "illustrative": w = "illustrative, no RBOT run"; break;
      case "synthetic": w = "synthetic portfolio data" + (d.ref ? " " + d.ref : ""); break;
      default: w = d.prov || "";
    }
    if (d.projected) w = "projected, " + w;
    return w;
  }
  function soft(d) { return d && (d.prov === "model" || d.prov === "illustrative"); }
  function gapText(d) { return "n/a, " + ((d && d.reason) || "not in the sources"); }
  function niceStep(range, count) {
    var raw = range / Math.max(count, 1);
    var p = Math.pow(10, Math.floor(Math.log10(raw)));
    var r = raw / p;
    return (r <= 1 ? 1 : r <= 2 ? 2 : r <= 2.5 ? 2.5 : r <= 5 ? 5 : 10) * p;
  }
  function scaleOf(values, count, includeZero) {
    var lo = Math.min.apply(null, values), hi = Math.max.apply(null, values);
    if (includeZero !== false) { lo = Math.min(0, lo); hi = Math.max(0, hi); }
    if (!isFinite(lo) || !isFinite(hi)) { lo = 0; hi = 1; }
    if (lo === hi) { hi = lo + 1; }
    var step = niceStep(hi - lo, count || 5);
    var a = Math.floor(lo / step + 1e-9) * step, b = Math.ceil(hi / step - 1e-9) * step;
    var ticks = [];
    for (var t = a; t <= b + step / 2; t += step) ticks.push(Math.round(t / step) * step);
    return { lo: a, hi: b, ticks: ticks, step: step };
  }
  function fmtTick(t, step) {
    var d = step < 1 ? Math.min(2, decimals(String(Number(step.toFixed(6))))) : 0;
    var txt = Math.abs(t).toLocaleString("en-US", { minimumFractionDigits: d, maximumFractionDigits: d });
    return t < 0 ? "−" + txt : txt;
  }

  /* ------------------------------------------------------------ text measurement */
  var canvas = null;
  function tw(text, size, weight) {
    if (!canvas) canvas = document.createElement("canvas").getContext("2d");
    canvas.font = (weight || 400) + " " + (size || 12) + "px Inter, system-ui, sans-serif";
    return canvas.measureText(String(text)).width;
  }
  function wrap(text, maxW, size, maxLines) {
    var words = String(text).split(/\s+/), lines = [], cur = "";
    words.forEach(function (w) {
      var next = cur ? cur + " " + w : w;
      if (tw(next, size) <= maxW || !cur) cur = next;
      else { lines.push(cur); cur = w; }
    });
    if (cur) lines.push(cur);
    lines = lines.map(function (ln) {
      if (tw(ln, size) <= maxW) return ln;
      while (ln.length > 2 && tw(ln + "\u2026", size) > maxW) ln = ln.slice(0, -1);
      return ln + "\u2026";
    });
    if (maxLines && lines.length > maxLines) {
      lines = lines.slice(0, maxLines);
      lines[maxLines - 1] = lines[maxLines - 1] + "…";
    }
    return lines;
  }
  function textLines(x, y, lines, attrs, lh) {
    var t = s("text", Object.assign({ x: x, y: y }, attrs || {}));
    lines.forEach(function (ln, i) { t.appendChild(s("tspan", { x: x, dy: i === 0 ? 0 : (lh || 12), text: ln })); });
    return t;
  }

  /* ------------------------------------------------------------ palette */
  var FALLBACK = {
    "chart-1": "#0017E5", "chart-2": "#C4410C", "chart-3": "#000533", "chart-4": "#55585E",
    "chart-5": "#2B8FD6", "chart-neutral": "#8D939D", "chart-critical": "#A6100F",
    "chart-grid": "#E1E3E6", "chart-axis": "#55585E", "risk-low": "#F0F2F5", "risk-med": "#CBE4FE",
    "risk-high": "#F6D4D2", "soft-blue": "#CBE4FE", "navy": "#000533", "positive": "#0F8048"
  };
  function color(name) {
    var key = typeof name === "number" ? "chart-" + name : String(name || "chart-1");
    if (key === "neutral" || key === "critical") key = "chart-" + key;
    if (key.charAt(0) === "#") return key;
    var v = getComputedStyle(document.documentElement).getPropertyValue("--" + key).trim();
    return v || FALLBACK[key] || FALLBACK["chart-1"];
  }
  var ON_DARK = { "chart-1": true, "chart-2": true, "chart-3": true, "chart-4": true, "chart-critical": true };
  function seriesColor(series, i) {
    if (series && series.color) return series.color;
    return i < 5 ? i + 1 : "neutral";
  }
  var SHAPES = ["circle", "square", "diamond", "triangle", "cross"];

  /* ------------------------------------------------------------ frame */
  /* roving focus across a chart's marks: Tab enters once, arrow keys move, Home and End jump */
  function markFocus(e) {
    var g = e.target.closest ? e.target.closest("g.mark") : null;
    if (!g) return;
    Array.prototype.forEach.call(e.currentTarget.querySelectorAll("g.mark"), function (m) { m.setAttribute("tabindex", m === g ? "0" : "-1"); });
  }
  function markArrows(e) {
    var step = e.key === "ArrowRight" || e.key === "ArrowDown" ? 1 : e.key === "ArrowLeft" || e.key === "ArrowUp" ? -1 : 0;
    var jump = e.key === "Home" ? 0 : e.key === "End" ? -1 : null;
    if (!step && jump === null) return;
    var list = Array.prototype.slice.call(e.currentTarget.querySelectorAll("g.mark")), i = list.indexOf(e.target.closest("g.mark"));
    if (i < 0) return;
    var next = jump !== null ? (jump < 0 ? list.length - 1 : 0) : Math.max(0, Math.min(list.length - 1, i + step));
    e.preventDefault();
    list[next].focus();
  }
  function mount(el, spec, kind) {
    if (!el) throw new Error("RBOTCharts." + kind.name + ": no element");
    var id = "rc" + (++uid);
    while (el.firstChild) el.removeChild(el.firstChild);
    var level = Math.min(6, Math.max(2, spec.headingLevel || 4));
    var fig = h("figure", { class: "chart chart--" + kind.name, id: spec.id || id, "data-chart": kind.name });
    var head = h("div", { class: "chart__head" }, [
      spec.number ? h("span", { class: "chart__num", text: spec.number }) : null,
      h("h" + level, { class: "chart__title", text: spec.title || "" }),
      spec.summary ? h("p", { class: "chart__summary", text: spec.summary }) : null
    ]);
    var plot = h("div", { class: "chart__plot" });
    var tip = h("div", { class: "chart__tip", role: "status", hidden: true });
    var legend = h("ul", { class: "chart__legend", "aria-label": "Legend" });
    var twinId = id + "-twin";
    var toggle = h("button", {
      type: "button", class: "btn btn--quiet chart__toggle", "aria-expanded": "false", "aria-controls": twinId,
      text: "Show table"
    });
    var twin = h("div", { class: "chart__twin", id: twinId, hidden: true });
    toggle.addEventListener("click", function () {
      var open = toggle.getAttribute("aria-expanded") !== "true";
      toggle.setAttribute("aria-expanded", String(open));
      toggle.textContent = open ? "Hide table" : "Show table";
      twin.hidden = !open;
    });
    add(fig, [head, plot, h("div", { class: "chart__foot" }, [legend, toggle]), twin,
      spec.source ? h("p", { class: "chart__source", text: "Source: " + spec.source }) : null]);
    el.appendChild(fig);

    var ctx = { id: id, spec: spec, plot: plot, tip: tip, defs: null, patterns: {} };
    function draw() {
      while (plot.firstChild) plot.removeChild(plot.firstChild);
      var W = Math.max(280, Math.round(plot.clientWidth || el.clientWidth || 640));
      var svg = s("svg", { role: "group", "aria-label": (spec.title || kind.name) + ", chart; each mark is focusable" });
      ctx.svg = svg; ctx.W = W; ctx.patterns = {};
      svg.addEventListener("keydown", markArrows);
      svg.addEventListener("focusin", markFocus);
      ctx.defs = s("defs");
      svg.appendChild(ctx.defs);
      var H = kind.draw(ctx, spec);
      var marks = svg.querySelectorAll("g.mark");
      for (var mi = 1; mi < marks.length; mi++) marks[mi].setAttribute("tabindex", "-1");  /* one tab stop per chart; arrows move between marks */
      svg.setAttribute("viewBox", "0 0 " + W + " " + H);
      svg.setAttribute("width", W);
      svg.setAttribute("height", H);
      plot.appendChild(svg);
      plot.appendChild(tip);
    }
    function fill() {
      while (legend.firstChild) legend.removeChild(legend.firstChild);
      kind.legend(spec).concat(provLegend(kind.datums(spec))).forEach(function (e) { legend.appendChild(legendItem(e)); });
      while (twin.firstChild) twin.removeChild(twin.firstChild);
      twin.appendChild(h("div", { class: "table-scroll" }, [kind.twin(spec)]));
    }
    fill();
    draw();
    var last = plot.clientWidth, raf = 0;
    var ro = typeof ResizeObserver === "function" ? new ResizeObserver(function () {
      if (Math.abs(plot.clientWidth - last) < 2) return;
      last = plot.clientWidth;
      cancelAnimationFrame(raf);
      raf = requestAnimationFrame(draw);
    }) : null;
    if (ro) ro.observe(plot);
    if (document.fonts && document.fonts.ready) document.fonts.ready.then(function () { draw(); });
    return {
      element: fig,
      redraw: draw,
      update: function (next) { spec = next; ctx.spec = next; fill(); draw(); },
      destroy: function () { if (ro) ro.disconnect(); if (fig.parentNode) fig.parentNode.removeChild(fig); }
    };
  }

  /* hatch pattern for model-authored / illustrative fills */
  function hatch(ctx, c) {
    var key = c.replace("#", "");
    if (ctx.patterns[key]) return "url(#" + ctx.patterns[key] + ")";
    var pid = ctx.id + "-h-" + key;
    ctx.defs.appendChild(s("pattern", { id: pid, width: 5, height: 5, patternUnits: "userSpaceOnUse", patternTransform: "rotate(45)" }, [
      s("rect", { width: 5, height: 5, fill: "#fff" }),
      s("line", { x1: 0, y1: 0, x2: 0, y2: 5, stroke: c, "stroke-width": 2 })
    ]));
    ctx.patterns[key] = pid;
    return "url(#" + pid + ")";
  }
  /* fill + stroke attributes for a datum's provenance */
  function paint(ctx, c, d) {
    if (soft(d)) return { fill: hatch(ctx, c), stroke: c, "stroke-width": 1.25, "stroke-dasharray": "3 2" };
    return { fill: c };
  }

  /* a focusable mark: shape(s) plus a >= 24px hit rect */
  function mark(ctx, box, label, ref, kids) {
    var g = s("g", { class: "mark", tabindex: 0, role: "img", "aria-label": label, "data-ref": ref || null });
    add(g, kids);
    var w = Math.max(24, box.w), hh = Math.max(24, box.h);
    g.appendChild(s("rect", { class: "hit", x: box.x + box.w / 2 - w / 2, y: box.y + box.h / 2 - hh / 2, width: w, height: hh, rx: 2 }));
    function show() {
      ctx.tip.textContent = label + (ref ? ". Press Enter or click for the source." : "");
      ctx.tip.hidden = false;
      var pr = ctx.plot.getBoundingClientRect(), mr = g.getBoundingClientRect();
      var tipW = Math.min(288, ctx.tip.offsetWidth || 200);
      var left = Math.min(Math.max(0, mr.left - pr.left + mr.width / 2 - tipW / 2), pr.width - tipW);
      var top = mr.top - pr.top - (ctx.tip.offsetHeight || 40) - 6;
      if (top < -10) top = mr.bottom - pr.top + 6;
      ctx.tip.style.left = left + "px";
      ctx.tip.style.top = top + "px";
    }
    function hide() { ctx.tip.hidden = true; }
    function press(e) {
      if (ref && window.RBOTUI) { window.RBOTUI.open(ref, g); hide(); }
      else show();
      if (e) e.preventDefault();
    }
    g.addEventListener("mouseenter", show);
    g.addEventListener("mouseleave", hide);
    g.addEventListener("focus", show);
    g.addEventListener("blur", hide);
    g.addEventListener("click", press);
    g.addEventListener("keydown", function (e) {
      if (e.key === "Enter" || e.key === " ") press(e);
      if (e.key === "Escape") hide();
    });
    ctx.svg.appendChild(g);
    return g;
  }
  function pointShape(shape, x, y, r, attrs) {
    switch (shape) {
      case "square": return s("rect", Object.assign({ x: x - r * 0.9, y: y - r * 0.9, width: r * 1.8, height: r * 1.8 }, attrs));
      case "diamond": return s("path", Object.assign({ d: "M" + x + " " + (y - r * 1.2) + "L" + (x + r * 1.2) + " " + y + "L" + x + " " + (y + r * 1.2) + "L" + (x - r * 1.2) + " " + y + "Z" }, attrs));
      case "triangle": return s("path", Object.assign({ d: "M" + x + " " + (y - r * 1.2) + "L" + (x + r * 1.15) + " " + (y + r * 0.9) + "L" + (x - r * 1.15) + " " + (y + r * 0.9) + "Z" }, attrs));
      case "cross": return s("path", Object.assign({ d: "M" + (x - r) + " " + (y - r) + "L" + (x + r) + " " + (y + r) + "M" + (x + r) + " " + (y - r) + "L" + (x - r) + " " + (y + r), "stroke-width": 2 }, attrs, { fill: "none" }));
      default: return s("circle", Object.assign({ cx: x, cy: y, r: r }, attrs));
    }
  }
  function pointAttrs(c, d) {
    return soft(d) ? { fill: "#fff", stroke: c, "stroke-width": 1.75 } : { fill: c, stroke: c, "stroke-width": 1 };
  }

  /* ------------------------------------------------------------ axes */
  function yAxis(ctx, sc, y, left, right, unit, unitY) {
    var g = s("g", { class: "grid ax", "aria-hidden": "true" });
    sc.ticks.forEach(function (t) {
      var yy = Math.round(y(t)) + 0.5;
      g.appendChild(s("line", { x1: left, x2: right, y1: yy, y2: yy }));
      g.appendChild(s("text", { x: left - 6, y: yy + 3.5, "text-anchor": "end", text: fmtTick(t, sc.step) }));
    });
    if (unit) g.appendChild(s("text", { x: left - 6, y: unitY === undefined ? y(sc.hi) - 10 : unitY, "text-anchor": "end", class: "lbl--muted", text: unit }));
    ctx.svg.appendChild(g);
    if (sc.lo <= 0 && sc.hi >= 0) ctx.svg.appendChild(s("line", { class: "zero", x1: left, x2: right, y1: Math.round(y(0)) + 0.5, y2: Math.round(y(0)) + 0.5, "aria-hidden": "true" }));
  }
  function xAxisValues(ctx, sc, x, top, bottom, unit) {
    var g = s("g", { class: "grid ax", "aria-hidden": "true" });
    sc.ticks.forEach(function (t) {
      var xx = Math.round(x(t)) + 0.5;
      g.appendChild(s("line", { x1: xx, x2: xx, y1: top, y2: bottom }));
      g.appendChild(s("text", { x: xx, y: bottom + 14, "text-anchor": "middle", text: fmtTick(t, sc.step) }));
    });
    if (unit) g.appendChild(s("text", { x: x(sc.hi), y: bottom + 28, "text-anchor": "end", class: "lbl--muted", text: unit }));
    ctx.svg.appendChild(g);
    if (sc.lo <= 0 && sc.hi >= 0) ctx.svg.appendChild(s("line", { class: "zero", x1: Math.round(x(0)) + 0.5, x2: Math.round(x(0)) + 0.5, y1: top, y2: bottom, "aria-hidden": "true" }));
  }
  /* a fiscal-year label that would touch its neighbour reads FY23 instead of FY2023 */
  function fitCat(c, band) { return /^FY20\d\d$/.test(c) && tw(c, 12) > band - 4 ? c.replace(/^FY20/, "FY") : c; }
  function catLabels(ctx, cats, xOf, band, y, maxLines) {
    var lines = cats.map(function (c) { return wrap(fitCat(c, band), Math.max(46, band - 6), 12, maxLines || 2); });
    var g = s("g", { class: "ax", "aria-hidden": "true" });
    cats.forEach(function (c, i) { g.appendChild(textLines(xOf(i), y, lines[i], { "text-anchor": "middle" }, 14)); });
    ctx.svg.appendChild(g);
    return Math.max.apply(null, lines.map(function (l) { return l.length; }));
  }
  function maxLinesFor(cats, band, maxLines) {
    return Math.max.apply(null, cats.map(function (c) { return wrap(fitCat(c, band), Math.max(46, band - 6), 12, maxLines || 2).length; }));
  }
  function gapMark(ctx, x, y, label, ref) {
    var w = tw("n/a", 12, 600) + 6;
    return mark(ctx, { x: x - w / 2, y: y - 11, w: w, h: 14 }, label, ref, [
      s("text", { class: "na", x: x, y: y, "text-anchor": "middle", text: "n/a" })
    ]);
  }

  /* ------------------------------------------------------------ legend */
  function legendItem(e) {
    var c = e.color ? color(e.color) : color("chart-neutral");
    var sw = s("svg", { width: 22, height: 12, viewBox: "0 0 22 12", "aria-hidden": "true" });
    var pid = "lg" + (++uid);
    switch (e.kind) {
      case "line": sw.appendChild(s("line", { x1: 1, x2: 21, y1: 6, y2: 6, stroke: c, "stroke-width": 2 })); if (e.shape) sw.appendChild(pointShape(e.shape, 11, 6, 3.2, { fill: c, stroke: c })); break;
      case "dashed": sw.appendChild(s("line", { x1: 1, x2: 21, y1: 6, y2: 6, stroke: c, "stroke-width": 2, "stroke-dasharray": "4 3" })); break;
      case "hollow": sw.appendChild(pointShape(e.shape || "circle", 11, 6, 4, { fill: "#fff", stroke: c, "stroke-width": 1.75 })); break;
      case "dot": sw.appendChild(pointShape(e.shape || "circle", 11, 6, 4, { fill: c, stroke: c })); break;
      case "rule": sw.appendChild(s("line", { x1: 11, x2: 11, y1: 0, y2: 12, stroke: c, "stroke-width": 2 })); break;
      case "hatch":
        sw.appendChild(s("defs", {}, [s("pattern", { id: pid, width: 5, height: 5, patternUnits: "userSpaceOnUse", patternTransform: "rotate(45)" }, [
          s("rect", { width: 5, height: 5, fill: "#fff" }), s("line", { x1: 0, y1: 0, x2: 0, y2: 5, stroke: c, "stroke-width": 2 })])]));
        sw.appendChild(s("rect", { x: 3, y: 1, width: 16, height: 10, fill: "url(#" + pid + ")", stroke: c, "stroke-dasharray": "3 2" }));
        break;
      case "na": sw.appendChild(s("text", { x: 11, y: 10, "text-anchor": "middle", "font-size": 12, "font-style": "italic", "font-weight": 600, fill: "#55585E", text: "n/a" })); break;
      default: sw.appendChild(s("rect", { x: 3, y: 1, width: 16, height: 10, fill: c }));
    }
    return h("li", { class: e.kind === "na" ? "lg-na" : null }, [sw, e.label]);
  }
  function provLegend(datums) {
    var out = [], seen = {};
    datums.forEach(function (d) {
      if (!d) return;
      if (d.projected) seen.proj = true;
      if (soft(d)) seen[d.prov] = true;
      if (isGap(d)) seen.gap = true;
    });
    if (seen.proj) out.push({ kind: "dashed", color: "chart-axis", label: "Projected" });
    if (seen.model) out.push({ kind: "hatch", color: "chart-4", label: "Model-authored (hatched or hollow)" });
    if (seen.illustrative) out.push({ kind: "hatch", color: "chart-4", label: "Illustrative, no RBOT run (hatched or hollow)" });
    if (seen.gap) out.push({ kind: "na", label: "Not in the sources (reason on the mark)" });
    return out;
  }

  /* ------------------------------------------------------------ table twin */
  function chipFor(d) {
    if (!d || !d.ref) return null;
    var cls = d.prov === "calculated" ? "calc" : (d.ref.charAt(0) === "G" ? "gap" : "cite");
    if (cls === "gap") return h("button", { type: "button", class: "gapref", "data-ref": d.ref, "aria-label": "Gap " + d.ref + ": not in the sources, open the reason", text: d.ref });
    return h("button", { type: "button", class: cls, "data-ref": d.ref, "aria-label": (cls === "calc" ? "Calculation " : "Citation ") + d.ref, text: d.ref });
  }
  function valueCell(d, unit, opts) {
    var td = h("td", { class: "num" });
    if (!d) return td;
    if (isMissing(d) || (isGap(d) && d.reason)) {
      var g = h(d.ref ? "button" : "span", { class: "gap", type: d.ref ? "button" : null, "data-ref": d.ref || null },
        [h("span", { class: "gap__reason", text: d.reason || "not in the sources" })]);
      td.classList.remove("num");
      td.appendChild(g);
      return td;
    }
    td.appendChild(document.createTextNode(shown(d, opts && opts.unitInCell ? unit : null, "table").text));
    var chip = chipFor(d);
    if (chip) td.appendChild(chip);
    if (d.prov === "illustrative") td.appendChild(h("span", { class: "illus", text: "Illustrative" }));
    if (d.prov === "model") td.appendChild(h("span", { class: "tag-model", text: "Model" }));
    if (d.projected) td.appendChild(h("span", { class: "gap__reason", text: " proj." }));
    return td;
  }
  function table(caption, headers, rows) {
    var t = h("table", { class: "dt dt--framed" });
    t.appendChild(h("caption", { class: "vh", text: caption + ", table" }));
    t.appendChild(h("thead", {}, [h("tr", {}, headers.map(function (x, i) {
      var parts = String(x).split(" | ");
      return h("th", { scope: "col", class: i === 0 ? null : "num" }, [parts[0], parts[1] ? h("span", { class: "unit", text: parts[1] }) : null]);
    }))]));
    var tb = h("tbody");
    rows.forEach(function (r) { tb.appendChild(r); });
    t.appendChild(tb);
    return t;
  }
  function rowHead(text) { return h("th", { scope: "row", text: text }); }
  function textCell(text) { return h("td", { text: text == null ? "" : text }); }

  /* ================================================================ lineStrip */
  var lineStrip = {
    name: "lineStrip",
    datums: function (sp) { return [].concat.apply([], sp.series.map(function (x) { return x.values; })); },
    legend: function (sp) {
      return sp.series.map(function (x, i) {
        return { kind: "line", color: seriesColor(x, i), shape: x.shape || SHAPES[i % 5], label: x.label };
      });
    },
    twin: function (sp) {
      return table(sp.title, [sp.categoryLabel || "Period"].concat(sp.series.map(function (x) { return x.label + " | " + (sp.unit || ""); })),
        sp.categories.map(function (c, i) {
          return h("tr", {}, [rowHead(c)].concat(sp.series.map(function (x) { return valueCell(x.values[i], sp.unit); })));
        }));
    },
    draw: function (ctx, sp) {
      var W = ctx.W, H = sp.height || 220, n = sp.categories.length;
      var vals = [];
      sp.series.forEach(function (x) { x.values.forEach(function (d) { if (!isGap(d)) vals.push(parseNum(d.v)); }); });
      var sc = scaleOf(vals, sp.ticks || 4, sp.includeZero);
      var left = Math.max.apply(null, sc.ticks.map(function (t) { return tw(fmtTick(t, sc.step)); })) + 12;
      left = Math.max(left, tw(sp.unit || "", 12) + 8);
      var endW = 0;
      sp.series.forEach(function (x) {
        var lastD = null;
        x.values.forEach(function (d) { if (!isGap(d)) lastD = d; });
        if (lastD && sp.labels !== "none") endW = Math.max(endW, tw(withUnit(lastD.v, sp.unit === "x" || sp.unit === "%" ? sp.unit : ""), 12, 600));
      });
      var right = W - Math.max(12, endW + 14);
      var step = (right - left) / n;
      var bLines = maxLinesFor(sp.categories, step, 2);
      /* a category every series misses for the same reason gets one n/a mark, not one per series */
      var merged = sp.categories.map(function (c, i) {
        if (sp.series.length < 2 || !sp.series.every(function (x) { return isGap(x.values[i]); })) return false;
        var r0 = sp.series[0].values[i] && sp.series[0].values[i].reason;
        return sp.series.every(function (x) { return (x.values[i] && x.values[i].reason) === r0; });
      });
      var gapsPerCat = sp.categories.map(function (c, i) { return merged[i] ? 1 : sp.series.filter(function (x) { return isGap(x.values[i]); }).length; });
      var maxGaps = Math.max.apply(null, gapsPerCat);
      var top = 24 + Math.max(0, maxGaps - 1) * 15 + (maxGaps > 0 ? 6 : 0);   /* n/a labels sit on their own rows, clear of the unit label */
      var bottom = H - 10 - bLines * 14;
      var y = function (v) { return bottom - (v - sc.lo) / (sc.hi - sc.lo) * (bottom - top); };
      var x = function (i) { return left + step * (i + 0.5); };
      yAxis(ctx, sc, y, left, right, sp.unit, maxGaps > 0 ? 10 : undefined);
      catLabels(ctx, sp.categories, x, step, bottom + 15, 2);
      /* projected divider */
      var firstProj = -1;
      for (var i = 0; i < n && firstProj < 0; i++) {
        if (sp.series.some(function (x2) { return x2.values[i] && x2.values[i].projected; })) firstProj = i;
      }
      if (firstProj > 0) {
        var px = Math.round(left + step * firstProj) + 0.5;
        ctx.svg.appendChild(s("line", { x1: px, x2: px, y1: top - 6, y2: bottom, stroke: color("chart-axis"), "stroke-dasharray": "2 3", "aria-hidden": "true" }));
        ctx.svg.appendChild(s("text", { x: px + 4, y: top - 10, class: "lbl--muted", "aria-hidden": "true", text: "Projected" }));
      }
      var ends = [];
      sp.series.forEach(function (ser, si) {
        var c = color(seriesColor(ser, si)), shape = ser.shape || SHAPES[si % 5];
        var g = s("g", { "aria-hidden": "true" });
        for (var j = 0; j < n - 1; j++) {
          var a = ser.values[j], b = ser.values[j + 1];
          if (isGap(a) || isGap(b)) continue;
          var dashed = b.projected || soft(a) || soft(b);
          g.appendChild(s("line", { x1: x(j), y1: y(parseNum(a.v)), x2: x(j + 1), y2: y(parseNum(b.v)), stroke: c, "stroke-width": 2, "stroke-dasharray": dashed ? "5 4" : null, "stroke-linecap": "butt" }));
        }
        ctx.svg.appendChild(g);
        ser.values.forEach(function (d, j) {
          var cat = sp.categories[j];
          if (isGap(d)) {
            if (merged[j] && si > 0) return;
            var k = merged[j] ? 0 : sp.series.slice(0, si).filter(function (x2) { return isGap(x2.values[j]); }).length;
            var gy = top - 8 + k * 15;
            if (k === 0) ctx.svg.appendChild(s("line", { x1: x(j), x2: x(j), y1: gy + 4, y2: bottom, stroke: color("chart-neutral"), "stroke-dasharray": "1 3", "aria-hidden": "true" }));
            gapMark(ctx, x(j), gy, (merged[j] ? sp.series.map(function (x2) { return x2.label; }).join(" and ") : ser.label) + ", " + cat + ": " + gapText(d), d && d.ref);
            return;
          }
          var vy = y(parseNum(d.v));
          mark(ctx, { x: x(j) - 5, y: vy - 5, w: 10, h: 10 },
            ser.label + ", " + cat + ": " + withUnit(d.v, sp.unit) + " (" + provWord(d) + ")", d.ref,
            [pointShape(shape, x(j), vy, 3.6, pointAttrs(c, d))]);
        });
        var lastJ = -1;
        ser.values.forEach(function (d, j) { if (!isGap(d)) lastJ = j; });
        if (lastJ >= 0 && sp.labels !== "none") ends.push({ y: y(parseNum(ser.values[lastJ].v)), x: x(lastJ), text: withUnit(ser.values[lastJ].v, sp.unit === "x" || sp.unit === "%" ? sp.unit : ""), c: c });
      });
      ends.sort(function (a, b) { return a.y - b.y; });
      for (var e = 1; e < ends.length; e++) if (ends[e].y - ends[e - 1].y < 15) ends[e].y = ends[e - 1].y + 15;
      ends.forEach(function (en) {
        ctx.svg.appendChild(s("text", { x: en.x + 8, y: en.y + 4, class: "lbl", fill: en.c, style: "fill:" + en.c, "aria-hidden": "true", text: en.text }));
      });
      return H;
    }
  };

  /* ================================================================ columns (grouped) */
  var columns = {
    name: "columns",
    datums: lineStrip.datums,
    legend: function (sp) { return sp.series.map(function (x, i) { return { kind: "fill", color: seriesColor(x, i), label: x.label }; }); },
    twin: lineStrip.twin,
    draw: function (ctx, sp) {
      var W = ctx.W, H = sp.height || 240, n = sp.categories.length, m = sp.series.length;
      var vals = [];
      sp.series.forEach(function (x) { x.values.forEach(function (d) { if (!isGap(d)) vals.push(parseNum(d.v)); }); });
      var sc = scaleOf(vals, sp.ticks || 4, true);
      var left = Math.max.apply(null, sc.ticks.map(function (t) { return tw(fmtTick(t, sc.step)); })) + 12;
      left = Math.max(left, tw(sp.unit || "", 12) + 8);
      var right = W - 8, band = (right - left) / n;
      var bLines = maxLinesFor(sp.categories, band, 2);
      var top = 22, bottom = H - 10 - bLines * 14;
      var y = function (v) { return bottom - (v - sc.lo) / (sc.hi - sc.lo) * (bottom - top); };
      yAxis(ctx, sc, y, left, right, sp.unit);
      var inner = band * 0.78, barW = Math.min(56, inner / m), gap = Math.min(4, barW * 0.12);
      catLabels(ctx, sp.categories, function (i) { return left + band * (i + 0.5); }, band, bottom + 15, 2);
      sp.categories.forEach(function (cat, i) {
        var gx = left + band * (i + 0.5) - (barW * m) / 2;
        sp.series.forEach(function (ser, si) {
          var d = ser.values[i], c = color(seriesColor(ser, si)), bx = gx + barW * si + gap / 2, bw = barW - gap;
          if (isGap(d)) { gapMark(ctx, bx + bw / 2, y(0) - 5, ser.label + ", " + cat + ": " + gapText(d), d && d.ref); return; }
          var v = parseNum(d.v), y0 = y(0), y1 = y(v), top1 = Math.min(y0, y1), hgt = Math.max(1, Math.abs(y1 - y0));
          var kids = [s("rect", Object.assign({ x: bx, y: top1, width: bw, height: hgt }, paint(ctx, c, d)))];
          var lbl = String(d.v);
          if (sp.labels !== false && tw(lbl, 12, 600) <= barW + 8) {
            kids.push(s("text", { class: "lbl", x: bx + bw / 2, y: v >= 0 ? top1 - 4 : top1 + hgt + 12, "text-anchor": "middle", text: lbl }));
          }
          mark(ctx, { x: bx, y: top1, w: bw, h: hgt }, ser.label + ", " + cat + ": " + withUnit(d.v, sp.unit) + " (" + provWord(d) + ")", d.ref, kids);
        });
      });
      return H;
    }
  };

  /* ================================================================ waterfall */
  var waterfall = {
    name: "waterfall",
    datums: function (sp) { return sp.steps.map(function (x) { return x.d; }); },
    legend: function (sp) {
      var out = [{ kind: "fill", color: "chart-3", label: sp.totalLabel || "Total" },
        { kind: "fill", color: "chart-1", label: "Increase" }, { kind: "fill", color: "chart-2", label: "Decrease" }];
      if (sp.steps.some(function (x) { return x.kind === "residual"; })) out.push({ kind: "fill", color: "chart-critical", label: "Unexplained residual" });
      return out;
    },
    twin: function (sp) {
      return table(sp.title, [sp.categoryLabel || "Step", "Kind", "Amount | " + (sp.unit || "")],
        sp.steps.map(function (st) {
          var kind = st.kind === "total" ? "Total" : st.kind === "residual" ? "Unexplained residual" :
            isGap(st.d) ? "Step" : parseNum(st.d.v) >= 0 ? "Increase" : "Decrease";
          return h("tr", { class: st.kind === "total" ? "total" : null }, [rowHead(st.label), textCell(kind), valueCell(st.d, sp.unit)]);
        }));
    },
    draw: function (ctx, sp) {
      var W = ctx.W, H = sp.height || 260, n = sp.steps.length;
      var level = 0, bars = [], vals = [0];
      sp.steps.forEach(function (st) {
        if (isGap(st.d)) { bars.push({ st: st, gap: true, at: level }); return; }
        var v = parseNum(st.d.v);
        if (st.kind === "total") { bars.push({ st: st, a: 0, b: v }); level = v; }
        else { bars.push({ st: st, a: level, b: level + v }); level += v; }
        vals.push(bars[bars.length - 1].a, bars[bars.length - 1].b);
      });
      var sc = scaleOf(vals, sp.ticks || 4, true);
      var left = Math.max.apply(null, sc.ticks.map(function (t) { return tw(fmtTick(t, sc.step)); })) + 12;
      left = Math.max(left, tw(sp.unit || "", 12) + 8);
      var right = W - 8, band = (right - left) / n;
      var labels = sp.steps.map(function (st) { var l = st.short || st.label; return st.kind === "residual" ? l + " (unexplained)" : l; });
      var bLines = maxLinesFor(labels, band, 3);
      var top = 22, bottom = H - 10 - bLines * 14;
      var y = function (v) { return bottom - (v - sc.lo) / (sc.hi - sc.lo) * (bottom - top); };
      yAxis(ctx, sc, y, left, right, sp.unit);
      catLabels(ctx, labels, function (i) { return left + band * (i + 0.5); }, band, bottom + 15, 3);
      var bw = Math.min(64, band * 0.62);
      bars.forEach(function (b, i) {
        var cx = left + band * (i + 0.5), bx = cx - bw / 2, st = b.st;
        if (b.gap) { gapMark(ctx, cx, y(b.at) - 6, st.label + ": " + gapText(st.d), st.d && st.d.ref); return; }
        var v = parseNum(st.d.v);
        var cname = st.kind === "total" ? "chart-3" : st.kind === "residual" ? "chart-critical" : v >= 0 ? "chart-1" : "chart-2";
        var c = color(cname), y0 = y(b.a), y1 = y(b.b), t0 = Math.min(y0, y1), hg = Math.max(1, Math.abs(y1 - y0));
        if (i < bars.length - 1 && !bars[i + 1].gap) {
          var ly = Math.round(y(b.b)) + 0.5;
          ctx.svg.appendChild(s("line", { x1: bx + bw, x2: left + band * (i + 1.5) - bw / 2, y1: ly, y2: ly, stroke: color("chart-neutral"), "stroke-dasharray": "2 2", "aria-hidden": "true" }));
        }
        var up = st.kind === "total" ? true : v >= 0;
        var word = st.kind === "total" ? "total" : st.kind === "residual" ? "unexplained residual" : v >= 0 ? "increase" : "decrease";
        mark(ctx, { x: bx, y: t0, w: bw, h: hg }, st.label + ", " + word + ": " + withUnit(st.d.v, sp.unit) + " (" + provWord(st.d) + ")", st.d.ref, [
          s("rect", Object.assign({ x: bx, y: t0, width: bw, height: hg }, paint(ctx, c, st.d))),
          s("text", { class: "lbl", x: cx, y: up ? t0 - 4 : t0 + hg + 12, "text-anchor": "middle", style: st.kind === "residual" ? "fill:" + c : null, text: String(st.d.v) })
        ]);
      });
      return H;
    }
  };

  /* ================================================================ horizontal helpers */
  function hLayout(ctx, sp, rows, values, rowH, extraRight) {
    var W = ctx.W;
    var labW = Math.min(W * 0.34, Math.max.apply(null, rows.map(function (r) { return tw(r.label, 12, 600); })) + 14);
    var sub = rows.some(function (r) { return r.sub; });
    var sc = scaleOf(values, sp.ticks || 5, sp.includeZero);
    var left = labW, right = W - (extraRight || 16), top = 8;
    var bottom = top + rows.length * rowH;
    var x = function (v) { return left + (v - sc.lo) / (sc.hi - sc.lo) * (right - left); };
    xAxisValues(ctx, sc, x, top, bottom, sp.unit);
    var g = s("g", { "aria-hidden": "true" });
    rows.forEach(function (r, i) {
      var cy = top + rowH * (i + 0.5);
      var lines = wrap(r.label, labW - 12, 12, 2);
      g.appendChild(textLines(labW - 10, cy + (sub ? -2 : 4) - (lines.length - 1) * 6, lines, { "text-anchor": "end", class: "lbl" }, 12));
      if (r.sub) g.appendChild(s("text", { x: labW - 10, y: cy + 11 + (lines.length - 1) * 6, "text-anchor": "end", class: "lbl--muted", text: r.sub }));
    });
    ctx.svg.appendChild(g);
    return { x: x, top: top, bottom: bottom, H: bottom + 36, cy: function (i) { return top + rowH * (i + 0.5); } };
  }

  /* ================================================================ bullet */
  var bullet = {
    name: "bullet",
    datums: function (sp) { return [].concat.apply([], sp.rows.map(function (r) { return [r.current, r.threshold]; })); },
    legend: function () { return [{ kind: "fill", color: "chart-1", label: "Current" }, { kind: "rule", color: "chart-3", label: "Threshold (ceiling or floor)" }]; },
    twin: function (sp) {
      return table(sp.title, [sp.categoryLabel || "Test", "Direction", "Threshold | " + (sp.unit || ""), "Current | " + (sp.unit || ""), "Headroom | " + (sp.unit || "")],
        sp.rows.map(function (r) {
          return h("tr", {}, [rowHead(r.label), textCell(dirWord(r.direction)), valueCell(r.threshold, sp.unit), valueCell(r.current, sp.unit), valueCell(r.headroom, sp.unit)]);
        }));
    },
    draw: function (ctx, sp) {
      var vals = [];
      sp.rows.forEach(function (r) { [r.current, r.threshold].forEach(function (d) { if (!isGap(d)) vals.push(parseNum(d.v)); }); });
      if (!vals.length) vals.push(1);
      var rows = sp.rows.map(function (r) { return { label: r.label, sub: dirWord(r.direction) }; });
      var short = sp.unit === "x" || sp.unit === "%" ? sp.unit : "";
      var tlw = 0;
      sp.rows.forEach(function (r) { if (!isGap(r.threshold)) tlw = Math.max(tlw, tw(dirWord(r.direction) + " " + withUnit(r.threshold.v, short), 12)); });
      var anyGap = sp.rows.some(function (r) { return isGap(r.threshold); });
      var L = hLayout(ctx, sp, rows, vals, anyGap ? 60 : 46, Math.max(20, tlw / 2 + 8));
      sp.rows.forEach(function (r, i) {
        var cy = L.cy(i) - (anyGap ? 6 : 0), c = color("chart-1");
        if (isGap(r.current) && isGap(r.threshold)) {
          var gd = r.threshold && r.threshold.reason ? r.threshold : r.current;
          var tx = L.x(0) + 6, gl = wrap("n/a: " + ((gd && gd.reason) || "not in the sources"), ctx.W - tx - 20, 12, 2);
          mark(ctx, { x: tx - 3, y: cy - 10, w: Math.min(ctx.W - tx - 10, tw(gl[0], 12) + 6), h: 14 * gl.length + 8 }, r.label + ": " + gapText(gd), (gd && gd.ref) || null,
            [textLines(tx, cy + 4 - (gl.length - 1) * 6, gl, { class: "na" }, 14)]);
          return;
        }
        var tx2 = isGap(r.threshold) ? null : Math.round(L.x(parseNum(r.threshold.v))) + 0.5;
        if (isGap(r.current)) gapMark(ctx, L.x(0) + 14, cy + 4, r.label + ", current: " + gapText(r.current), r.current && r.current.ref);
        else {
          var v = parseNum(r.current.v), x0 = L.x(0), x1 = L.x(v), bw = Math.abs(x1 - x0);
          var lbl = withUnit(r.current.v, short), lw = tw(lbl, 12, 600);
          var lx = Math.max(x0, x1) + 5, anchor = "start", fill = null;
          if (tx2 !== null && tx2 > lx - 8 && tx2 < lx + lw + 6) {
            if (bw > lw + 10) { lx = Math.max(x0, x1) - 5; anchor = "end"; fill = "fill:#fff"; }
            else lx = tx2 + 6;
          }
          mark(ctx, { x: Math.min(x0, x1), y: cy - 7, w: bw, h: 14 },
            r.label + ": current " + withUnit(r.current.v, sp.unit) + (isGap(r.threshold) ? "" : " against a " + dirWord(r.direction) + " of " + withUnit(r.threshold.v, sp.unit)) +
            (r.headroom && !isGap(r.headroom) ? ", headroom " + withUnit(r.headroom.v, sp.unit) : "") + " (" + provWord(r.current) + ")", r.current.ref, [
              s("rect", Object.assign({ x: Math.min(x0, x1), y: cy - 7, width: Math.max(1, bw), height: 14 }, paint(ctx, c, r.current))),
              s("text", { class: fill ? "lbl lbl--in" : "lbl", x: lx, y: cy + 4, "text-anchor": anchor, style: soft(r.current) ? null : fill, text: lbl })
            ]);
        }
        if (isGap(r.threshold)) {
          var gx = L.x(0) + 2, gl2 = wrap(dirWord(r.direction) + ": n/a, " + ((r.threshold && r.threshold.reason) || "not in the sources"), ctx.W - gx - 12, 12, 2);
          mark(ctx, { x: gx - 2, y: cy + 10, w: Math.min(ctx.W - gx - 8, tw(gl2[0], 12) + 4), h: 14 * gl2.length + 2 }, r.label + ", " + dirWord(r.direction) + ": " + gapText(r.threshold), r.threshold && r.threshold.ref,
            [textLines(gx, cy + 21, gl2, { class: "na" }, 14)]);
        } else {
          var tc = color("chart-3"), tl = dirWord(r.direction) + " " + withUnit(r.threshold.v, short), tlx = tx2 + 4, tanchor = "start";
          if (tlx + tw(tl, 12) > ctx.W - 2) { tlx = tx2 - 4; tanchor = "end"; }
          mark(ctx, { x: tx2 - 2, y: cy - 15, w: 4, h: 30 }, r.label + ": " + dirWord(r.direction) + " " + withUnit(r.threshold.v, sp.unit) + " (" + provWord(r.threshold) + ")", r.threshold.ref, [
            s("line", { x1: tx2, x2: tx2, y1: cy - 13, y2: cy + 13, stroke: tc, "stroke-width": 2.5, "stroke-dasharray": soft(r.threshold) ? "3 2" : null }),
            s("text", { class: "lbl--muted", x: tlx, y: cy - 12, "text-anchor": tanchor, text: tl })
          ]);
        }
      });
      return L.H;
    }
  };
  function dirWord(dir) { return dir === "max" ? "ceiling" : dir === "min" ? "floor" : "threshold, direction not stated"; }

  /* ================================================================ stackedColumns */
  var stackedColumns = {
    name: "stackedColumns",
    datums: lineStrip.datums,
    legend: columns.legend,
    twin: function (sp) {
      var hdr = [sp.categoryLabel || "Year"].concat(sp.series.map(function (x) { return x.label + " | " + (sp.unit || ""); }));
      if (sp.totals !== false) hdr.push("Total | " + (sp.unit || "") + ", calculated");
      return table(sp.title, hdr, sp.categories.map(function (c, i) {
        var cells = [rowHead(c)].concat(sp.series.map(function (x) { return valueCell(x.values[i], sp.unit); }));
        if (sp.totals !== false) cells.push(h("td", { class: "num", text: totalOf(sp, i) }));
        return h("tr", {}, cells);
      }));
    },
    draw: function (ctx, sp) {
      var W = ctx.W, H = sp.height || 260, n = sp.categories.length;
      var sums = sp.categories.map(function (c, i) {
        var t = 0; sp.series.forEach(function (x) { var d = x.values[i]; if (!isGap(d)) t += Math.max(0, parseNum(d.v)); }); return t;
      });
      var sc = scaleOf(sums, sp.ticks || 4, true);
      var left = Math.max.apply(null, sc.ticks.map(function (t) { return tw(fmtTick(t, sc.step)); })) + 12;
      left = Math.max(left, tw(sp.unit || "", 12) + 8);
      var right = W - 8, band = (right - left) / n;
      var bLines = maxLinesFor(sp.categories, band, 2);
      var top = 22, bottom = H - 10 - bLines * 14;
      var y = function (v) { return bottom - (v - sc.lo) / (sc.hi - sc.lo) * (bottom - top); };
      yAxis(ctx, sc, y, left, right, sp.unit);
      catLabels(ctx, sp.categories, function (i) { return left + band * (i + 0.5); }, band, bottom + 15, 2);
      var bw = Math.min(64, band * 0.66);
      sp.categories.forEach(function (cat, i) {
        var cx = left + band * (i + 0.5), bx = cx - bw / 2, acc = 0, gaps = [];
        sp.series.forEach(function (ser, si) {
          var d = ser.values[i];
          if (!d) return;
          if (isGap(d)) { gaps.push({ ser: ser, d: d }); return; }
          var v = parseNum(d.v);
          if (v === 0) return;
          var cname = seriesColor(ser, si), c = color(cname), y0 = y(acc), y1 = y(acc + v), hg = Math.max(1, y0 - y1);
          var kids = [s("rect", Object.assign({ x: bx, y: y1, width: bw, height: hg }, paint(ctx, c, d), { stroke: "#fff", "stroke-width": soft(d) ? 1.25 : 0.75 }))];
          if (hg >= 14 && tw(String(d.v), 12, 600) <= bw - 4) {
            var key = typeof cname === "number" ? "chart-" + cname : cname;
            kids.push(s("text", { class: "lbl lbl--in", x: cx, y: y1 + hg / 2 + 4, "text-anchor": "middle", style: "font-size:12px;fill:" + (ON_DARK[key] && !soft(d) ? "#fff" : "#000533"), text: String(d.v) }));
          }
          mark(ctx, { x: bx, y: y1, w: bw, h: hg }, ser.label + ", " + cat + ": " + withUnit(d.v, sp.unit) + " (" + provWord(d) + ")", d.ref, kids);
          acc += v;
        });
        var topY = y(acc);
        if (sp.totals !== false && acc > 0) {
          ctx.svg.appendChild(s("text", { class: "lbl", x: cx, y: topY - 4, "text-anchor": "middle", "aria-hidden": "true", text: totalOf(sp, i) }));
        }
        gaps.forEach(function (gp, k) {
          gapMark(ctx, cx, topY - 18 - k * 14, gp.ser.label + ", " + cat + ": " + gapText(gp.d), gp.d.ref);
        });
      });
      return H;
    }
  };
  function totalOf(sp, i) {
    var vs = [];
    sp.series.forEach(function (x) { var d = x.values[i]; if (!isGap(d)) vs.push(d.v); });
    return vs.length ? sumExact(vs) : "";
  }

  /* ================================================================ rangeStrip */
  var STATS = ["min", "q1", "median", "q3", "max"];
  var rangeStrip = {
    name: "rangeStrip",
    datums: function (sp) {
      var out = [];
      sp.rows.forEach(function (r) { STATS.concat("marker").forEach(function (k) { if (r[k]) out.push(r[k]); }); });
      return out;
    },
    legend: function (sp) {
      return [{ kind: "fill", color: "soft-blue", label: "Interquartile range (Q1 to Q3)" },
        { kind: "rule", color: "chart-3", label: "Median" }, { kind: "rule", color: "chart-neutral", label: "Min and max" },
        { kind: "dot", color: "chart-1", label: sp.markerLabel || "Issuer" }];
    },
    twin: function (sp) {
      var present = STATS.filter(function (k) { return sp.rows.some(function (r) { return r[k]; }); });
      var names = { min: "Min", q1: "Q1", median: "Median", q3: "Q3", max: "Max" };
      return table(sp.title, [sp.categoryLabel || "Metric"].concat(present.map(function (k) { return names[k] + " | " + (sp.unit || ""); }), [(sp.markerLabel || "Issuer") + " | " + (sp.unit || "")]),
        sp.rows.map(function (r) {
          return h("tr", {}, [rowHead(r.label)].concat(present.map(function (k) { return valueCell(r[k], sp.unit); }), [valueCell(r.marker, sp.unit)]));
        }));
    },
    draw: function (ctx, sp) {
      var vals = [];
      rangeStrip.datums(sp).forEach(function (d) { if (!isGap(d)) vals.push(parseNum(d.v)); });
      var L = hLayout(ctx, sp, sp.rows.map(function (r) { return { label: r.label, sub: r.sub }; }), vals, 48, 24);
      var neutral = color("chart-neutral"), navy = color("chart-3"), blue = color("chart-5"), issuer = color("chart-1");
      sp.rows.forEach(function (r, i) {
        var cy = L.cy(i);
        var lo = r.min && !isGap(r.min) ? parseNum(r.min.v) : null, hi = r.max && !isGap(r.max) ? parseNum(r.max.v) : null;
        if (lo !== null && hi !== null) ctx.svg.appendChild(s("line", { x1: L.x(lo), x2: L.x(hi), y1: cy, y2: cy, stroke: neutral, "stroke-width": 1, "aria-hidden": "true" }));
        if (r.q1 && r.q3) {
          if (isGap(r.q1) || isGap(r.q3)) gapMark(ctx, L.x(0) + 14, cy + 4, r.label + ", interquartile range: " + gapText(isGap(r.q1) ? r.q1 : r.q3), null);
          else {
            var a = L.x(parseNum(r.q1.v)), b = L.x(parseNum(r.q3.v));
            mark(ctx, { x: a, y: cy - 8, w: b - a, h: 16 }, r.label + ": interquartile range " + withUnit(r.q1.v, sp.unit) + " to " + withUnit(r.q3.v, sp.unit) + " (" + provWord(r.q1) + ")", r.q1.ref, [
              s("rect", { x: a, y: cy - 8, width: Math.max(1, b - a), height: 16, fill: color("soft-blue"), stroke: blue, "stroke-width": 1, "stroke-dasharray": soft(r.q1) ? "3 2" : null })
            ]);
          }
        }
        [["min", neutral, 12, "Min"], ["max", neutral, 12, "Max"], ["median", navy, 20, "Median"]].forEach(function (cfg) {
          var d = r[cfg[0]];
          if (!d) return;
          if (isGap(d)) { gapMark(ctx, L.x(0) + 40, cy - 12, r.label + ", " + cfg[3].toLowerCase() + ": " + gapText(d), d.ref); return; }
          var xx = Math.round(L.x(parseNum(d.v))) + 0.5;
          mark(ctx, { x: xx - 2, y: cy - cfg[2] / 2, w: 4, h: cfg[2] }, r.label + ", " + cfg[3].toLowerCase() + ": " + withUnit(d.v, sp.unit) + " (" + provWord(d) + ")", d.ref, [
            s("line", { x1: xx, x2: xx, y1: cy - cfg[2] / 2, y2: cy + cfg[2] / 2, stroke: cfg[1], "stroke-width": cfg[0] === "median" ? 2.5 : 2, "stroke-dasharray": soft(d) ? "3 2" : null })
          ]);
        });
        if (r.marker) {
          if (isGap(r.marker)) { gapMark(ctx, L.x(0) + 70, cy - 12, r.label + ", " + (sp.markerLabel || "issuer") + ": " + gapText(r.marker), r.marker.ref); return; }
          var mx = L.x(parseNum(r.marker.v));
          mark(ctx, { x: mx - 6, y: cy - 6, w: 12, h: 12 }, r.label + ", " + (sp.markerLabel || "Issuer") + ": " + withUnit(r.marker.v, sp.unit) + " (" + provWord(r.marker) + ")", r.marker.ref, [
            pointShape("circle", mx, cy, 5.5, Object.assign(pointAttrs(issuer, r.marker), { stroke: "#fff", "stroke-width": soft(r.marker) ? 0 : 1.5 })),
            soft(r.marker) ? pointShape("circle", mx, cy, 5.5, { fill: "#fff", stroke: issuer, "stroke-width": 2 }) : null,
            s("text", { class: "lbl", x: mx, y: cy + 20, "text-anchor": "middle", style: "fill:" + issuer, text: (sp.markerLabel || "Issuer") + " " + withUnit(r.marker.v, sp.unit === "x" || sp.unit === "%" ? sp.unit : "") })
          ]);
        }
      });
      return L.H;
    }
  };

  /* ================================================================ scatter (spread curve) */
  function toYears(xv) {
    if (typeof xv === "number") return xv;
    var t = Date.parse(xv);
    return isNaN(t) ? NaN : t / (365.25 * 864e5) + 1970;
  }
  var scatter = {
    name: "scatter",
    datums: function (sp) { return sp.points.map(function (p) { return p.y; }); },
    groups: function (sp) {
      var g = [];
      sp.points.forEach(function (p) { if (g.indexOf(p.group) < 0) g.push(p.group); });
      return g;
    },
    legend: function (sp) {
      var gs = scatter.groups(sp);
      var out = gs.map(function (g, i) { return { kind: "dot", color: (sp.groupColors && sp.groupColors[g]) || (i < 5 ? i + 1 : "neutral"), shape: SHAPES[i % 5], label: g }; });
      if (sp.curve) out.push({ kind: sp.curve.prov === "calculated" || !sp.curve.prov ? "line" : "dashed", color: (sp.groupColors && sp.groupColors[sp.curve.group]) || "chart-neutral", label: sp.curve.label || "Fitted curve" });
      return out;
    },
    twin: function (sp) {
      return table(sp.title, ["Security", sp.groupLabel || "Group", sp.xLabel || "Maturity", (sp.yLabel || "Value") + " | " + (sp.unit || "")],
        sp.points.map(function (p) {
          var placed = !isNaN(toYears(p.x));
          return h("tr", {}, [rowHead(p.label), textCell(p.group), textCell(placed ? String(p.x) : String(p.x) + " (not placed: date not readable)"), valueCell(p.y, sp.unit)]);
        }));
    },
    draw: function (ctx, sp) {
      var W = ctx.W, H = sp.height || 300;
      var gs = scatter.groups(sp);
      var pts = sp.points.map(function (p) { return { p: p, x: toYears(p.x), y: isGap(p.y) ? NaN : parseNum(p.y.v) }; });
      var ok = pts.filter(function (q) { return !isNaN(q.x) && !isNaN(q.y); });
      var sc = scaleOf(ok.map(function (q) { return q.y; }), sp.ticks || 5, true);
      var xs = ok.map(function (q) { return q.x; });
      var xlo = Math.floor(Math.min.apply(null, xs.concat(sp.xMin !== undefined ? [sp.xMin] : [])));
      var xhi = Math.ceil(Math.max.apply(null, xs.concat(sp.xMax !== undefined ? [sp.xMax] : [])));
      if (xlo === xhi) xhi += 1;
      var left = Math.max.apply(null, sc.ticks.map(function (t) { return tw(fmtTick(t, sc.step)); })) + 12;
      left = Math.max(left, tw(sp.unit || "", 12) + 8);
      var right = W - 70, top = 16, bottom = H - 40;
      var y = function (v) { return bottom - (v - sc.lo) / (sc.hi - sc.lo) * (bottom - top); };
      var x = function (v) { return left + (v - xlo) / (xhi - xlo) * (right - left); };
      yAxis(ctx, sc, y, left, right, sp.unit);
      var ax = s("g", { class: "ax grid", "aria-hidden": "true" });
      var xstep = Math.max(1, Math.ceil((xhi - xlo) / 8));
      for (var t = xlo; t <= xhi; t += xstep) {
        ax.appendChild(s("line", { x1: Math.round(x(t)) + 0.5, x2: Math.round(x(t)) + 0.5, y1: bottom, y2: bottom + 4 }));
        ax.appendChild(s("text", { x: x(t), y: bottom + 16, "text-anchor": "middle", text: String(t) }));
      }
      ax.appendChild(s("text", { x: right, y: bottom + 32, "text-anchor": "end", class: "lbl--muted", text: sp.xLabel || "Maturity" }));
      ctx.svg.appendChild(ax);
      /* fitted curve: least squares y = a + b ln(years from asOf); positions only, never printed */
      if (sp.curve) {
        var asOfY = toYears(sp.asOf || "2026-06-30");
        var cp = ok.filter(function (q) { return (sp.curve.group == null || q.p.group === sp.curve.group) && q.x - asOfY > 0.05; });
        if (cp.length >= 3) {
          var n = cp.length, sx = 0, sy = 0, sxx = 0, sxy = 0;
          cp.forEach(function (q) { var l = Math.log(q.x - asOfY); sx += l; sy += q.y; sxx += l * l; sxy += l * q.y; });
          var b = (n * sxy - sx * sy) / (n * sxx - sx * sx), a = (sy - b * sx) / n;
          var mn = Math.min.apply(null, cp.map(function (q) { return q.x; })), mx2 = Math.max.apply(null, cp.map(function (q) { return q.x; }));
          var dPath = "";
          for (var k = 0; k <= 40; k++) {
            var xv = mn + (mx2 - mn) * k / 40, yv = a + b * Math.log(xv - asOfY);
            dPath += (k ? "L" : "M") + x(xv).toFixed(1) + " " + y(yv).toFixed(1);
          }
          var cc = color((sp.groupColors && sp.groupColors[sp.curve.group]) || "chart-neutral");
          ctx.svg.appendChild(s("path", { d: dPath, fill: "none", stroke: cc, "stroke-width": 1.5, "stroke-dasharray": soft({ prov: sp.curve.prov }) ? "5 4" : null, opacity: 0.8, "aria-hidden": "true" }));
        }
      }
      var placed = [];
      function collides(b) { return placed.some(function (o) { return b.x < o.x + o.w && b.x + b.w > o.x && b.y < o.y + o.h && b.y + b.h > o.y; }); }
      ok.sort(function (a2, b2) { return a2.x - b2.x; });
      ok.forEach(function (q) { placed.push({ x: x(q.x) - 6, y: y(q.y) - 6, w: 12, h: 12 }); });
      ok.forEach(function (q) {
        var gi = gs.indexOf(q.p.group), c = color((sp.groupColors && sp.groupColors[q.p.group]) || (gi < 5 ? gi + 1 : "neutral"));
        var px = x(q.x), py = y(q.y), kids = [pointShape(SHAPES[gi % 5], px, py, 4.5, pointAttrs(c, q.p.y))];
        var text = q.p.short || q.p.label, w = tw(text, 12, 600), hh = 14;
        var cands = [[px + 8, py - 6], [px - 8 - w, py - 6], [px - w / 2, py - 20], [px - w / 2, py + 8]];
        for (var ci = 0; ci < cands.length; ci++) {
          var bx = { x: cands[ci][0], y: cands[ci][1], w: w, h: hh };
          if (bx.x < left || bx.x + w > W - 2 || bx.y < 0 || collides(bx)) continue;
          placed.push(bx);
          kids.push(s("text", { class: "lbl", x: bx.x, y: bx.y + 10, style: "font-size:12px;fill:" + c, text: text }));
          break;
        }
        mark(ctx, { x: px - 5, y: py - 5, w: 10, h: 10 }, q.p.label + " (" + q.p.group + "), " + (sp.xLabel || "maturity") + " " + q.p.x + ": " + withUnit(q.p.y.v, sp.unit) + " (" + provWord(q.p.y) + ")", q.p.y.ref, kids);
      });
      var missing = pts.length - ok.length;
      if (missing) ctx.svg.appendChild(s("text", { x: left, y: H - 4, class: "na", text: missing + " point" + (missing > 1 ? "s" : "") + " not placed (n/a); reasons in the table" }));
      return H;
    }
  };

  /* ================================================================ dumbbell */
  var dumbbell = {
    name: "dumbbell",
    datums: function (sp) { return [].concat.apply([], sp.rows.map(function (r) { return [r.from, r.to]; })); },
    legend: function (sp) { return [{ kind: "hollow", color: "chart-neutral", label: sp.fromLabel || "From" }, { kind: "dot", color: "chart-1", label: sp.toLabel || "To" }]; },
    twin: function (sp) {
      var hasChg = sp.rows.some(function (r) { return r.change; });
      return table(sp.title, [sp.categoryLabel || "Category", (sp.fromLabel || "From") + " | " + (sp.unit || ""), (sp.toLabel || "To") + " | " + (sp.unit || "")].concat(hasChg ? [sp.changeLabel || "Change"] : []),
        sp.rows.map(function (r) {
          return h("tr", {}, [rowHead(r.label), valueCell(r.from, sp.unit), valueCell(r.to, sp.unit)].concat(hasChg ? [valueCell(r.change, "")] : []));
        }));
    },
    draw: function (ctx, sp) {
      var vals = [];
      dumbbell.datums(sp).forEach(function (d) { if (!isGap(d)) vals.push(parseNum(d.v)); });
      var maxLbl = Math.max.apply(null, dumbbell.datums(sp).map(function (d) { return isGap(d) ? 20 : tw(String(d.v), 12, 600); }));
      var L = hLayout(ctx, sp, sp.rows.map(function (r) { return { label: r.label, sub: r.sub }; }), vals, 34, maxLbl + 18);
      var grey = color("chart-neutral"), blue = color("chart-1");
      sp.rows.forEach(function (r, i) {
        var cy = L.cy(i);
        var a = isGap(r.from) ? null : L.x(parseNum(r.from.v)), b = isGap(r.to) ? null : L.x(parseNum(r.to.v));
        if (a !== null && b !== null) ctx.svg.appendChild(s("line", { x1: a, x2: b, y1: cy, y2: cy, stroke: grey, "stroke-width": 2.5, "aria-hidden": "true" }));
        var rightward = a === null || b === null || b >= a;
        if (a === null) gapMark(ctx, L.x(0) + 14, cy + 4, r.label + ", " + (sp.fromLabel || "from") + ": " + gapText(r.from), r.from && r.from.ref);
        else mark(ctx, { x: a - 6, y: cy - 6, w: 12, h: 12 }, r.label + ", " + (sp.fromLabel || "from") + ": " + withUnit(r.from.v, sp.unit) + " (" + provWord(r.from) + ")", r.from.ref, [
          pointShape("circle", a, cy, 5, { fill: "#fff", stroke: grey, "stroke-width": 2, "stroke-dasharray": soft(r.from) ? "2 1.5" : null }),
          s("text", { class: "lbl lbl--muted", x: rightward ? a - 9 : a + 9, y: cy + 4, "text-anchor": rightward ? "end" : "start", text: String(r.from.v) })
        ]);
        if (b === null) gapMark(ctx, L.x(0) + 40, cy + 4, r.label + ", " + (sp.toLabel || "to") + ": " + gapText(r.to), r.to && r.to.ref);
        else mark(ctx, { x: b - 6, y: cy - 6, w: 12, h: 12 }, r.label + ", " + (sp.toLabel || "to") + ": " + withUnit(r.to.v, sp.unit) + " (" + provWord(r.to) + ")", r.to.ref, [
          pointShape("circle", b, cy, 5.5, pointAttrs(blue, r.to)),
          s("text", { class: "lbl", x: rightward ? b + 9 : b - 9, y: cy + 4, "text-anchor": rightward ? "start" : "end", text: String(r.to.v) })
        ]);
      });
      return L.H;
    }
  };

  /* ================================================================ riskMatrix */
  var PROB = ["High", "Medium", "Low"], IMPACT = ["Low", "Medium", "High"];
  function level(text, list) {
    var t = String(text || "").trim().toLowerCase();
    for (var i = 0; i < list.length; i++) if (list[i].toLowerCase() === t) return list[i];
    return "Unknown";
  }
  var riskMatrix = {
    name: "riskMatrix",
    datums: function (sp) { return sp.events.map(function (e) { return { prov: e.prov, v: "1" }; }); },
    legend: function () {
      return [{ kind: "fill", color: "risk-low", label: "Low zone" }, { kind: "fill", color: "risk-med", label: "Medium zone" }, { kind: "fill", color: "risk-high", label: "High zone" }];
    },
    twin: function (sp) {
      return table(sp.title, ["Event", "Description", "Probability", "Impact", "Classification"], sp.events.map(function (e) {
        var desc = h("td", {}, [e.description || ""]);
        if (e.prov === "illustrative") desc.appendChild(h("span", { class: "illus", text: "Illustrative" }));
        if (e.ref) desc.appendChild(chipFor({ ref: e.ref, prov: e.prov }));
        return h("tr", {}, [rowHead(e.key + " " + e.label), desc, textCell(e.probability), textCell(e.impact), textCell(e.classification || "")]);
      }));
    },
    draw: function (ctx, sp) {
      var W = ctx.W;
      var probs = PROB.slice(), imps = IMPACT.slice();
      sp.events.forEach(function (e) {
        if (level(e.probability, PROB) === "Unknown" && probs.indexOf("Unknown") < 0) probs.push("Unknown");
        if (level(e.impact, IMPACT) === "Unknown" && imps.indexOf("Unknown") < 0) imps.push("Unknown");
      });
      var left = 92, top = 8, right = Math.min(W - 8, left + imps.length * 190);
      var cw = (right - left) / imps.length, ch = 66, bottom = top + probs.length * ch;
      var zoneName = { 0: "low", 1: "medium", 2: "high" };
      var ax = s("g", { class: "ax", "aria-hidden": "true" });
      probs.forEach(function (p, r) { ax.appendChild(s("text", { x: left - 10, y: top + ch * (r + 0.5) + 4, "text-anchor": "end", class: "lbl", text: p })); });
      imps.forEach(function (im, c) { ax.appendChild(s("text", { x: left + cw * (c + 0.5), y: bottom + 16, "text-anchor": "middle", class: "lbl", text: im })); });
      ax.appendChild(s("text", { x: 12, y: top + (bottom - top) / 2, transform: "rotate(-90 12 " + (top + (bottom - top) / 2) + ")", "text-anchor": "middle", class: "lbl--muted", text: "Probability" }));
      ax.appendChild(s("text", { x: left + (right - left) / 2, y: bottom + 32, "text-anchor": "middle", class: "lbl--muted", text: "Impact" }));
      ctx.svg.appendChild(ax);
      probs.forEach(function (p, r) {
        imps.forEach(function (im, c) {
          var pi = PROB.indexOf(p), ii = IMPACT.indexOf(im);
          var score = pi < 0 || ii < 0 ? -1 : (2 - pi) + ii; /* 0..4 */
          var zone = score < 0 ? null : score >= 3 ? 2 : score === 2 ? 1 : 0;
          var fill = zone === null ? "#fff" : color(["risk-low", "risk-med", "risk-high"][zone]);
          var x0 = left + cw * c, y0 = top + ch * r;
          ctx.svg.appendChild(s("rect", { x: x0, y: y0, width: cw, height: ch, fill: fill, stroke: "#fff", "stroke-width": 2, "aria-hidden": "true" }));
          var evs = sp.events.filter(function (e) { return level(e.probability, PROB) === p && level(e.impact, IMPACT) === im; });
          if (!evs.length) return;
          var soft2 = evs.some(function (e) { return soft(e); });
          var ids = evs.map(function (e) { return e.key; }).join(", ");
          var label = "Probability " + p + ", impact " + im + (zone === null ? "" : " (" + zoneName[zone] + " zone)") + ": " + evs.length + " event" + (evs.length > 1 ? "s" : "") + ", " +
            evs.map(function (e) { return e.key + " " + e.label; }).join("; ") + (soft2 ? " (illustrative, no RBOT run)" : "");
          mark(ctx, { x: x0 + 3, y: y0 + 3, w: cw - 6, h: ch - 6 }, label, null, [
            s("rect", { x: x0 + 3.5, y: y0 + 3.5, width: cw - 7, height: ch - 7, fill: "none", stroke: color("chart-3"), "stroke-width": 1, "stroke-dasharray": soft2 ? "3 2" : null }),
            s("text", { x: x0 + 12, y: y0 + 26, style: "font-family:var(--font-head);font-size:18px;font-weight:800;fill:#000533", text: String(evs.length) }),
            textLines(x0 + 12, y0 + 44, wrap(ids, cw - 24, 12, 2), { class: "lbl" }, 14)
          ]);
        });
      });
      return bottom + 40;
    }
  };

  window.RBOTCharts = {
    lineStrip: function (el, sp) { return mount(el, sp, lineStrip); },
    columns: function (el, sp) { return mount(el, sp, columns); },
    waterfall: function (el, sp) { return mount(el, sp, waterfall); },
    bullet: function (el, sp) { return mount(el, sp, bullet); },
    stackedColumns: function (el, sp) { return mount(el, sp, stackedColumns); },
    rangeStrip: function (el, sp) { return mount(el, sp, rangeStrip); },
    scatter: function (el, sp) { return mount(el, sp, scatter); },
    dumbbell: function (el, sp) { return mount(el, sp, dumbbell); },
    riskMatrix: function (el, sp) { return mount(el, sp, riskMatrix); },
    util: { parseNum: parseNum, sumExact: sumExact, withUnit: withUnit, provWord: provWord, isGap: isGap }
  };

  /* ================================================================ RBOTUI: popovers, chips, tabs */
  var pop = null, popAnchor = null;
  function data() { return window.RBOT_DATA || {}; }
  function lookup(ref) {
    var D = data();
    if (D.citations && D.citations[ref]) return { kind: D.citations[ref].synthetic ? "Synthetic portfolio file" : "Cited", item: D.citations[ref] };
    if (D.calcs && D.calcs[ref]) return { kind: "Calculated", item: D.calcs[ref] };
    if (D.gaps && D.gaps[ref]) return { kind: "Not in the sources", item: D.gaps[ref] };
    if (D.portfolio && D.portfolio.sources && D.portfolio.sources[ref]) return { kind: "Synthetic portfolio file", item: D.portfolio.sources[ref] };
    return null;
  }
  function close(restore) {
    if (!pop || pop.hidden) return;
    pop.hidden = true;
    if (popAnchor) {
      if (popAnchor.setAttribute) popAnchor.setAttribute("aria-expanded", "false");
      if (restore && popAnchor.focus) popAnchor.focus();
    }
    popAnchor = null;
  }
  function open(ref, anchor) {
    var found = lookup(ref);
    if (!pop) {
      pop = h("div", { class: "pop", role: "dialog", "aria-modal": "false", tabindex: "-1", hidden: true });
      document.body.appendChild(pop);
    }
    if (popAnchor && popAnchor !== anchor && popAnchor.setAttribute) popAnchor.setAttribute("aria-expanded", "false");
    while (pop.firstChild) pop.removeChild(pop.firstChild);
    var closeBtn = h("button", { type: "button", class: "pop__close", text: "Close", onclick: function () { close(true); } });
    pop.appendChild(h("div", { class: "pop__head" }, [h("div", {}, [h("span", { class: "pop__id", text: ref + " " }), h("span", { class: "pop__kind", text: found ? found.kind : "Unknown reference" })]), closeBtn]));
    pop.setAttribute("aria-label", ref + (found ? ", " + found.kind : ""));
    if (!found) pop.appendChild(h("p", { text: "No record for " + ref + " in RBOT_DATA." }));
    else if (found.kind === "Cited" || found.kind === "Synthetic portfolio file") {
      var it = found.item, served = anchor.getAttribute ? anchor.getAttribute("data-served") : null;
      pop.appendChild(h("dl", {}, [
        it.label ? h("dt", { text: "Figure" }) : null, it.label ? h("dd", { text: it.label + (it.value ? ": " + it.value : "") }) : null,
        served ? h("dt", { text: "Served as" }) : null, served ? h("dd", { text: served }) : null,
        h("dt", { text: "File" }), h("dd", { text: it.file || "" }),
        h("dt", { text: "Locator" }), h("dd", { text: it.locator || (it.line ? "line " + it.line : "") })
      ]));
      if (it.excerpt) pop.appendChild(h("blockquote", { text: it.excerpt }));
    } else if (found.kind === "Calculated") {
      var c = found.item, inputs = h("dd"), servedC = anchor.getAttribute ? anchor.getAttribute("data-served") : null;
      (c.inputs || []).forEach(function (r) { inputs.appendChild(chip(r)); inputs.appendChild(document.createTextNode(" ")); });
      pop.appendChild(h("dl", {}, [
        c.label ? h("dt", { text: "Figure" }) : null, c.label ? h("dd", { text: c.label + (c.value ? ": " + c.value : "") }) : null,
        servedC ? h("dt", { text: "Served as" }) : null, servedC ? h("dd", { text: servedC }) : null,
        h("dt", { text: "Formula" }), h("dd", {}, [h("code", { text: c.formula || "" })]),
        h("dt", { text: "Inputs" }), inputs
      ]));
      if (c.note) pop.appendChild(h("p", { class: "gap__reason", text: c.note }));
    } else {
      var g = found.item;
      pop.appendChild(h("dl", {}, [h("dt", { text: "Field" }), h("dd", { text: g.field || g.label || "" }), h("dt", { text: "Reason" }), h("dd", { text: g.reason || "" })]));
    }
    pop.hidden = false;
    var r = anchor.getBoundingClientRect();
    var left = Math.min(window.scrollX + r.left, window.scrollX + document.documentElement.clientWidth - pop.offsetWidth - 12);
    var top = window.scrollY + r.bottom + 6;
    if (r.bottom + pop.offsetHeight + 12 > window.innerHeight && r.top > pop.offsetHeight + 12) top = window.scrollY + r.top - pop.offsetHeight - 6;
    pop.style.left = Math.max(8, left) + "px";
    pop.style.top = top + "px";
    popAnchor = anchor;
    if (anchor.setAttribute) anchor.setAttribute("aria-expanded", "true");
    pop.focus();
  }
  /* Display formatting is the page's business: a hook turns a datum into the text a reader sees, while the
     passport (popover) keeps the string exactly as served. hook(datum, unit, context, kind) returns text or null. */
  function setFormat(fn) { fmtHook = typeof fn === "function" ? fn : null; }
  function digitsOf(t) { return String(t).replace(/[^0-9.]/g, ""); }
  function shown(d, unit, ctx, kind) {
    var served = String(d.v), t = fmtHook ? fmtHook(d, unit, ctx, kind) : null;
    if (t === null || t === undefined) t = unit ? withUnit(d.v, unit) : served;
    return { text: t, served: digitsOf(t) !== digitsOf(served) ? served : null };
  }
  function hit() { return h("span", { class: "hit", "aria-hidden": "true" }); }
  function chip(ref, prov) {
    var cls = ref.charAt(0) === "K" ? "calc" : ref.charAt(0) === "G" ? "gapref" : "cite";
    if (cls === "gapref") return h("button", { type: "button", class: "gapref", "data-ref": ref, "aria-label": "Gap " + ref + ": not in the sources, open the reason" }, [ref, hit()]);
    return h("button", { type: "button", class: cls, "data-ref": ref, "aria-label": (cls === "calc" ? "Calculation " : "Citation ") + ref + (prov ? ", " + prov : "") }, [ref, hit()]);
  }
  /* value(datum, unit, context): the figure and its provenance, or the n/a gap with its reason.
     context "prose": the figure itself is the button and carries a corner mark; no bracket chip. */
  function value(d, unit, ctx) {
    var f = document.createDocumentFragment();
    if (isMissing(d)) {
      f.appendChild(h(d && d.ref ? "button" : "span", { type: d && d.ref ? "button" : null, class: "gap", "data-ref": d && d.ref || null }, [h("span", { class: "gap__reason", text: (d && d.reason) || "not in the sources" }), d && d.ref ? hit() : null]));
      return f;
    }
    var sh = shown(d, unit, ctx || "table", "value");
    if (ctx === "prose" || ctx === "figure") {
      /* a span, not a button: a figure inside a sentence must wrap with the text around it */
      if (d.ref) f.appendChild(h("span", { class: "figref prov--" + (d.prov || "cited"), role: "button", tabindex: 0, "data-ref": d.ref, "data-served": sh.served,
        "aria-label": sh.text + ", " + provWord(d) }, [sh.text]));
      else f.appendChild(h("span", { class: "num", text: sh.text }));
      return f;
    }
    f.appendChild(h("span", { class: "num", text: sh.text }));
    if (d.ref) f.appendChild(chip(d.ref));
    if (d.prov === "illustrative") f.appendChild(h("span", { class: "illus", text: "Illustrative" }));
    if (d.prov === "model") f.appendChild(h("span", { class: "tag-model", text: "Model" }));
    return f;
  }
  function tabs(root) {
    (root || document).querySelectorAll("[data-tabs]").forEach(function (box) {
      var list = box.querySelector(".tabs__list");
      if (!list || list.dataset.wired) return;
      list.dataset.wired = "1";
      list.setAttribute("role", "tablist");
      var btns = Array.prototype.slice.call(list.querySelectorAll(".tabs__tab"));
      function select(b, focus) {
        btns.forEach(function (o) {
          var on = o === b;
          o.setAttribute("aria-selected", String(on));
          o.tabIndex = on ? 0 : -1;
          var p = document.getElementById(o.getAttribute("aria-controls"));
          if (p) p.hidden = !on;
        });
        if (focus) b.focus();
      }
      btns.forEach(function (b, i) {
        b.setAttribute("role", "tab");
        var p = document.getElementById(b.getAttribute("aria-controls"));
        if (p) { p.setAttribute("role", "tabpanel"); p.setAttribute("aria-labelledby", b.id); p.tabIndex = 0; }
        b.addEventListener("click", function () { select(b); });
        b.addEventListener("keydown", function (e) {
          var k = e.key, j = k === "ArrowRight" ? i + 1 : k === "ArrowLeft" ? i - 1 : k === "Home" ? 0 : k === "End" ? btns.length - 1 : null;
          if (j === null) return;
          e.preventDefault();
          select(btns[(j + btns.length) % btns.length], true);
        });
      });
      select(btns.filter(function (b) { return b.getAttribute("aria-selected") === "true"; })[0] || btns[0]);
    });
  }
  var wired = false;
  function init(root) {
    tabs(root);
    if (wired) return;
    wired = true;
    document.addEventListener("click", function (e) {
      var t = e.target.closest ? e.target.closest("button[data-ref], .figref[data-ref]") : null;
      if (t) { e.preventDefault(); if (popAnchor === t && pop && !pop.hidden) close(false); else open(t.getAttribute("data-ref"), t); return; }
      if (pop && !pop.hidden && !pop.contains(e.target) && !(e.target.closest && e.target.closest(".mark"))) close(false);
    });
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape") { close(true); return; }
      var fr = e.target.closest ? e.target.closest(".figref[data-ref]") : null;
      if (fr && (e.key === "Enter" || e.key === " ")) { e.preventDefault(); fr.click(); return; }
      rvKeys(e);
    });
    document.addEventListener("focusin", rvFocus);
  }
  /* House scale badge. kind: "rec" | "score" | "val" ; pos 1..5 or null (Avoid, N/A). */
  var SCALE_WORDS = {
    rec: ["Strong OW", "Modest OW", "MW", "Modest UW", "Strong UW"],
    score: ["Strong", "Good", "Fair", "Weak", "Stressed"],
    val: ["Very attractive", "Attractive", "Fair", "Unattractive", "Very unattractive"]
  };
  function scale(o) {
    var pos = o.pos == null ? null : Number(o.pos);
    var word = o.word || (pos ? SCALE_WORDS[o.kind || "rec"][pos - 1] : "N/A");
    var tone = pos == null ? (word === "Avoid" ? "neg" : "none") : pos <= 2 ? "pos" : pos === 3 ? "mid" : "neg";
    var label = (o.label ? o.label + ": " : "") + (o.kind === "val" && pos ? "V" + pos : pos || "") + (pos ? " " : "") + word + (pos ? " (" + pos + " of 5" + (o.kind === "rec" ? ", 1 is Strong OW" : o.kind === "score" ? ", 1 is Strong" : ", 1 is Very attractive") + ")" : "") + (o.illustrative ? ", illustrative" : "");
    var meter = h("span", { class: "scale__meter", "aria-hidden": "true" });
    for (var i = 1; i <= 5; i++) meter.appendChild(h("i", { class: pos === i ? "on" : null }));
    var el = h("span", { class: "scale" + (o.size === "lg" ? " scale--lg" : ""), "data-scale": o.kind || "rec", "data-tone": tone, role: "img", "aria-label": label }, [
      h("span", { class: "scale__pos", "aria-hidden": "true", text: pos ? (o.kind === "val" ? "V" + pos : String(pos)) : "" }),
      h("span", { class: "scale__word", "aria-hidden": "true", text: word }),
      pos ? meter : null
    ]);
    return el;
  }
  var STATUS = { pass: "pass", fits: "pass", restricted: "restricted", watch: "watch", blocked: "blocked", breaches: "breach", breach: "breach", "n/a": "na" };
  /* the reader-facing word: qa_status Restricted reads "With limitations" (the internal data keeps Restricted) */
  var STATUS_LABEL = { restricted: "With limitations" };
  function statusLabel(word) { return STATUS_LABEL[String(word).toLowerCase()] || word; }
  function status(word) {
    return h("span", { class: "status status--" + (STATUS[String(word).toLowerCase()] || "na"), text: statusLabel(word) });
  }
  function illus(text) { return h("span", { class: "illus", title: "No RBOT run exists; this judgement is written for the mockup", text: text || "Illustrative" }); }
  /* Dense-table cell: the figure is the button, the td carries prov--<kind>. kind hints the format ("rate", "date"). */
  function cell(td, d, unit, kind) {
    td.classList.add("prov");
    if (isMissing(d)) {
      td.classList.add("prov--gap");
      if (td.classList.contains("num")) td.style.textAlign = "right";
      td.appendChild(h(d && d.ref ? "button" : "span", { type: d && d.ref ? "button" : null, class: "gap", "data-ref": d && d.ref || null,
        title: (d && d.reason) || "not in the sources", "aria-label": "n/a, " + ((d && d.reason) || "not in the sources") },
        [h("span", { class: "gap__reason", text: (d && d.reason) || "" }), d && d.ref ? hit() : null]));
      return td;
    }
    td.classList.add("prov--" + (d.prov || "cited"));
    var sh = shown(d, unit, "table", kind), txt = sh.text;
    if (d.ref) td.appendChild(h("button", { type: "button", class: "cellref", "data-ref": d.ref, "data-served": sh.served, "aria-label": txt + ", " + provWord(d) }, [txt, hit()]));
    else td.appendChild(h("span", { text: txt }));
    return td;
  }
  /* Roving focus: one tab stop per block of provenance buttons (a table, a list, a paragraph); arrow keys move within it. */
  var RV = "button.cellref, button.cite, button.calc, button.gap, button.gapref, .figref";
  function groupOf(b) { return b.closest("table, ol, ul, p, dl, figure, [data-roving]") || b.parentElement; }
  function roving(root) {
    var groups = [], seen = new Map();
    Array.prototype.forEach.call((root || document).querySelectorAll(RV), function (b) {
      var g = groupOf(b), list = seen.get(g);
      if (!list) { list = []; seen.set(g, list); groups.push(list); }
      list.push(b);
    });
    groups.forEach(function (list) {
      list.forEach(function (b, i) { b.tabIndex = i === 0 ? 0 : -1; b.setAttribute("data-rv", "1"); });
    });
    return groups.length;
  }
  function rvKeys(e) {
    var b = e.target.closest ? e.target.closest("[data-rv]") : null;
    if (!b) return;
    var dx = e.key === "ArrowRight" ? 1 : e.key === "ArrowLeft" ? -1 : 0, dy = e.key === "ArrowDown" ? 1 : e.key === "ArrowUp" ? -1 : 0;
    var home = e.key === "Home", end = e.key === "End";
    if (!dx && !dy && !home && !end) return;
    var g = groupOf(b), list = Array.prototype.filter.call(g.querySelectorAll(RV), function (x) { return groupOf(x) === g && x.offsetParent !== null; });
    var i = list.indexOf(b), next = null;
    if (i < 0) return;
    if (dy && g.tagName === "TABLE") {
      var td = b.closest("td, th"), tr = td && td.parentElement, col = td ? td.cellIndex : 0;
      for (var r = tr ? (dy > 0 ? tr.nextElementSibling : tr.previousElementSibling) : null; r && !next; r = dy > 0 ? r.nextElementSibling : r.previousElementSibling) {
        var c = r.cells[col], cand = c && c.querySelector(RV);
        if (cand && cand.offsetParent !== null) next = cand;
      }
    }
    if (!next) next = home ? list[0] : end ? list[list.length - 1] : list[Math.max(0, Math.min(list.length - 1, i + (dx || dy)))];
    if (next === b) return;
    e.preventDefault();
    next.focus();
  }
  function rvFocus(e) {
    var b = e.target.closest ? e.target.closest("[data-rv]") : null;
    if (!b) return;
    var g = groupOf(b);
    Array.prototype.forEach.call(g.querySelectorAll("[data-rv]"), function (x) { if (groupOf(x) === g) x.tabIndex = x === b ? 0 : -1; });
  }
  window.RBOTUI = { cell: cell, init: init, open: open, close: close, chip: chip, value: value, tabs: tabs, el: h, scale: scale, status: status, statusLabel: statusLabel, illus: illus, setFormat: setFormat, roving: roving };
})();
