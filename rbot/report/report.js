/* RBOT Report: shell behaviour and enhancement of the static page that rbotlib/report/html.py writes.
   The page is complete without this script (tables, chart twins, anchors). Here it adds hash routing
   between the views, search, a contents line, the "How to read a figure" popover, collapse/expand,
   the mobile menu, print, source and calculation popovers, scale and status badges, charts and the
   Model column toggles. Shared layer: RBOTUI and RBOTCharts (charts.js). Figures print as served: no
   display formatter is installed and no date is rewritten. Nodes are built through RBOTUI.el only; no network.
   Functions lifted from the frozen mockup design/mockups/report-a.js name their source line. */
(function () {
  "use strict";
  var UI = window.RBOTUI, C = window.RBOTCharts, el = UI.el;
  var main = document.getElementById("main");
  var run = JSON.parse(document.getElementById("rbot-run").textContent);
  var VIEWS = {}, ORDER = [], charts = [];
  var baseTitle = document.title;

  function all(sel, root) { return Array.prototype.slice.call((root || document).querySelectorAll(sel)); }
  function txt(s) { return document.createTextNode(s); }
  function plain(s) { return String(s).replace(/\s+/g, " ").trim(); }
  function swap(oldNode, newNode) { oldNode.parentNode.replaceChild(newNode, oldNode); }

  /* ------------------------------------------------------------ RBOT_DATA from the embedded rbot-run/1 JSON */
  /* The popovers read window.RBOT_DATA.{citations,calcs,gaps} by ref: "<MODULE>:C<n>" for a citation,
     "MODEL:<line>:<column>" for a Model cell passport, "MODEL:gap:<line>:<column>" for a Model gap. */
  function buildData() {
    var citations = {}, calcs = {}, gaps = {};
    function cite(module, c) {
      citations[module + ":" + c.id] = { file: c.source, locator: c.locator, excerpt: c.excerpt,
        label: module + " " + c.id + (c.anchored === false ? " (unanchored)" : "") };
    }
    Object.keys(run.handoffs).forEach(function (m) { run.handoffs[m].citations.forEach(function (c) { cite(m, c); }); });
    var brief = run.run_brief.tables.citations;
    if (brief) {
      brief.rows.forEach(function (row) {
        var c = {};
        brief.columns.forEach(function (name, i) { c[name] = row[i]; });
        cite("RUN_BRIEF", { id: c.id, source: c.source, locator: c.locator, excerpt: c.excerpt, anchored: null });
      });
    }
    var model = run.model, columns = {};
    (model ? model.columns : []).forEach(function (col) { columns[col.column_id] = col.label; });
    (model ? model.lines : []).forEach(function (line) {
      line.cells.forEach(function (cell) {
        var where = line.line_id + ":" + cell.column_id, label = line.label + ", " + columns[cell.column_id];
        if (cell.value === null) { gaps["MODEL:gap:" + where] = { field: label, reason: cell.reason }; return; }
        var inputs = [], loose = [];
        cell.sources.forEach(function (s) {
          if (s.citation_id) inputs.push(s.module + ":" + s.citation_id);
          else loose.push(s.source + " " + s.locator);
        });
        calcs["MODEL:" + where] = { label: label, value: cell.value, formula: cell.basis + (cell.note ? "; " + cell.note : ""),
          inputs: inputs, note: loose.length ? "Also from " + loose.join("; ") : null };
      });
    });
    return { citations: citations, calcs: calcs, gaps: gaps };
  }
  window.RBOT_DATA = buildData();

  /* ------------------------------------------------------------ views */
  all("section.view[data-view]", main).forEach(function (node) {
    var id = node.getAttribute("data-view"), h1 = node.querySelector(".vtitle");
    VIEWS[id] = { id: id, title: h1.textContent, el: node, h1: h1, nav: null, toc: [] };
    ORDER.push(id);
  });
  all("#nav a.nav__a[data-view]").forEach(function (a) { VIEWS[a.getAttribute("data-view")].nav = a; });

  /* report-a.js:383 viewTools: one button collapses or expands every section of a view */
  function viewTools(v) {
    var b = el("button", { type: "button", class: "btn btn--quiet vtools", text: "Collapse all" });
    function boxes() { return all("details.cb", v.el).filter(function (d) { return !d.hasAttribute("data-keep"); }); }
    function sync() { b.textContent = boxes().some(function (d) { return d.open; }) ? "Collapse all" : "Expand all"; }
    b.addEventListener("click", function () {
      var list = boxes(), any = list.some(function (d) { return d.open; });
      list.forEach(function (d) { d.open = !any; });
      sync();
    });
    v.el.addEventListener("toggle", sync, true);
    return b;
  }

  /* ------------------------------------------------------------ contents line (report-a.js:1379 buildToc) */
  var spy = { items: [] };
  function buildToc(v) {
    var items = [];
    all("details.cb[id], section.fold[id]", v.el).forEach(function (d) {
      if (d.parentElement && d.parentElement.closest("details.cb")) return;
      var h = d.querySelector(".cb__t, .fold__t");
      if (h) items.push({ el: d, label: h.textContent });
    });
    v.toc = items;
    var slot = v.el.querySelector(".toc-slot");
    if (items.length < 2 || !slot) return;
    var ul = el("ul", { class: "toc__list" }, items.map(function (it) {
      it.a = el("a", { href: "#" + it.el.id, text: it.label });
      return el("li", {}, [it.a]);
    }));
    slot.appendChild(el("nav", { class: "toc", "aria-label": "Sections of " + v.title }, [el("span", { class: "toc__k", text: "On this page" }), ul]));
  }
  var spyTimer = 0;
  function updateSpy() {   /* report-a.js:1392: the section in view carries aria-current="location" */
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

  /* ------------------------------------------------------------ How to read a figure (report-a.js:1417) */
  var keyPop = null, keyBtn = null;
  function buildKeyBody(host) {
    function row(mark, text) { return el("li", {}, [el("span", { class: "key__m" }, [mark]), el("span", { text: text })]); }
    function sw(cls) { return el("i", { class: "prov-swatch prov-swatch--" + cls, "aria-hidden": "true" }); }
    host.appendChild(el("ul", { class: "key__list" }, [
      row(sw("cited"), "Cited figure: select it for file, locator and excerpt"),
      row(sw("calculated"), "Calculated figure: select it for the formula and its inputs"),
      row(el("span", { class: "gap", "aria-hidden": "true", text: "n/a" }), "Missing from the sources, with its reason"),
      row(el("span", { class: "cite key__chip", "aria-hidden": "true", text: "C12" }), "Source note: select it for the citation"),
      row(el("span", { class: "tag-model", text: "Model" }), "Written by the model from cited figures")
    ]));
    host.appendChild(el("p", { class: "key__h", text: "House scales" }));
    host.appendChild(el("p", { class: "key__p" }, [UI.scale({ kind: "rec", pos: 2, word: "Modest OW", label: "Example" }),
      txt(" Position 1 is the strongest and 5 the weakest; the meter marks the position. The word carries the meaning; colour does not.")]));
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

  /* ------------------------------------------------------------ search (report-a.js:1528 indexSearch, runSearch, buildSearch) */
  /* Indexed: every section, every figure (once, in the view that numbered it first) and every citation.
     Calculations and gaps have no anchor in the static page, so they are not search targets. */
  var SEARCH = [];
  function indexSearch() {
    var seenFig = {};
    ORDER.forEach(function (id) {
      var v = VIEWS[id];
      all("details.cb[id], section.fold[id]", v.el).forEach(function (d) {
        if (d.parentElement && d.parentElement.closest("details.cb")) return;
        var h = d.querySelector(".cb__t, .fold__t");
        SEARCH.push({ kind: "Section", view: v.title, title: h ? h.textContent : d.id, target: d.id, text: plain(d.textContent) });
      });
      all("figure.chart[id]", v.el).forEach(function (f) {
        var n = f.querySelector(".chart__num"), t = f.querySelector(".chart__title"), s = f.querySelector(".chart__summary");
        var key = n ? n.textContent : f.id;
        if (seenFig[key]) return;
        seenFig[key] = true;
        SEARCH.push({ kind: "Figure", view: v.title, title: (n ? n.textContent + " " : "") + (t ? t.textContent : ""), target: f.id,
          text: plain((t ? t.textContent : "") + " " + (s ? s.textContent : "")) });
      });
    });
    var cites = window.RBOT_DATA.citations;
    Object.keys(cites).forEach(function (key) {
      var c = cites[key];
      SEARCH.push({ kind: "Citation", view: "Evidence", title: key, target: "ev-" + key.replace(":", "-"),
        text: plain([key, c.label, c.file, c.locator, c.excerpt].join(" ")) });
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
    var at = -1;
    for (var i = 0; i < words.length && at < 0; i++) at = e.low.indexOf(words[i]);
    var from = Math.max(0, at - 40), s = e.text.slice(from, from + 120);
    return (from > 0 ? "… " : "") + s + (from + 120 < e.text.length ? " …" : "");
  }
  function markWords(node, text, words) {
    var re = new RegExp("(" + words.map(function (w) { return w.replace(/[.*+?^${}()|[\]\\]/g, "\\$&"); }).join("|") + ")", "ig");
    text.split(re).forEach(function (part, i) { node.appendChild(i % 2 ? el("mark", { text: part }) : txt(part)); });
  }
  function buildSearch() {
    var input = document.getElementById("pane-search"), out = document.getElementById("pane-results");
    var status = el("p", { class: "vh", role: "status" });
    out.parentNode.insertBefore(status, out);
    function render() {
      var q = input.value.trim();
      while (out.firstChild) out.removeChild(out.firstChild);
      if (q.length < 2) { status.textContent = ""; out.hidden = true; return; }
      var words = q.toLowerCase().split(/\s+/).filter(Boolean), hits = runSearch(q);
      out.hidden = false;
      status.textContent = hits.length ? hits.length + (hits.length === 1 ? " result" : " results") : "No results";
      if (!hits.length) { out.appendChild(el("li", { class: "search__none", text: "Nothing in the Report matches “" + q + "”. Try a figure, a module name or a source id such as C12." })); return; }
      hits.forEach(function (hit) {
        var s = el("span", { class: "search__s" });
        var a = el("a", { class: "search__a", href: "#" + hit.e.target }, [
          el("span", { class: "search__k", text: hit.e.kind + " · " + hit.e.view }), el("span", { class: "search__t", text: hit.e.title }), s]);
        markWords(s, snippet(hit.e, words), words);
        out.appendChild(el("li", {}, [a]));
      });
    }
    input.addEventListener("input", render);
    input.addEventListener("keydown", function (e) {
      if (e.key === "ArrowDown") { var a = out.querySelector("a"); if (a) { e.preventDefault(); a.focus(); } }
      if (e.key === "Escape") { input.value = ""; render(); }
    });
    out.addEventListener("keydown", function (e) {
      var links = all("a", out), i = links.indexOf(document.activeElement);
      if (e.key === "ArrowDown" && i < links.length - 1) { e.preventDefault(); links[i + 1].focus(); }
      if (e.key === "ArrowUp") { e.preventDefault(); (i > 0 ? links[i - 1] : input).focus(); }
      if (e.key === "Escape") input.focus();
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

  /* ------------------------------------------------------------ router (report-a.js:1573 sheetOpen, 1613 route, show, reveal) */
  var activeId = null, traversal = false, scrolls = {};
  var menu = document.getElementById("pane-menu"), sheet = document.getElementById("pane-sheet");
  function sheetOpen(open) {
    menu.setAttribute("aria-expanded", String(open));
    document.getElementById("pane").classList.toggle("is-open", open);
  }
  function hashKey() { return location.hash || "#snapshot"; }
  function show(v, user) {
    if (activeId === v.id) return false;
    if (activeId) { VIEWS[activeId].el.hidden = true; if (VIEWS[activeId].nav) VIEWS[activeId].nav.removeAttribute("aria-current"); }
    activeId = v.id;
    v.el.hidden = false;
    if (v.nav) v.nav.setAttribute("aria-current", "page");
    document.title = v.title + " · " + baseTitle;
    document.getElementById("route-live").textContent = v.title;
    window.scrollTo(0, 0);
    if (user) v.h1.focus({ preventScroll: true });
    closeKey(false);
    charts.forEach(function (c) { c.redraw(); });
    spy = { items: v.toc };
    updateSpy();
    if (v.nav) {
      var r = v.nav.getBoundingClientRect(), pr = sheet.getBoundingClientRect();
      if (r.top < pr.top || r.bottom > pr.bottom) v.nav.scrollIntoView({ block: "nearest" });
    }
    return true;
  }
  /* open every closed section around the target, then bring it into view */
  function reveal(t, focus) {
    for (var p = t; p; p = p.parentElement) if (p.tagName === "DETAILS") p.open = true;
    requestAnimationFrame(function () {
      t.scrollIntoView({ block: "start" });
      updateSpy();
      if (focus) {
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

  /* ------------------------------------------------------------ print (report-a.js:1646) */
  /* The Snapshot is re-flowed into a grid and scaled to fit one landscape page; every view after it
     prints with every section open. */
  var PAGE_W = 985, PAGE_H = 712;   /* CSS px inside @page margins; fits both US Letter and A4 landscape */
  var wasOpen = null;
  function printPrepare() {
    if (wasOpen) return;
    var root = document.documentElement, snap = VIEWS.snapshot.el;
    wasOpen = [];
    all("details").forEach(function (d) { wasOpen.push([d, d.open]); d.open = true; });
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
    var snap = VIEWS.snapshot.el;
    document.documentElement.classList.remove("printing");
    snap.style.width = ""; snap.style.zoom = "";
    wasOpen.forEach(function (x) { x[0].open = x[1]; });
    wasOpen = null;
    charts.forEach(function (c) { c.redraw(); });
  }
  window.addEventListener("beforeprint", printPrepare);
  window.addEventListener("afterprint", printRestore);
  window.RBOTPrint = { prepare: printPrepare, restore: printRestore };

  /* ------------------------------------------------------------ enhancement of the static markup (D2), in document order */
  function enhanceScale(node) {
    var pos = node.getAttribute("data-pos"), box = node.closest(".call__item");
    var label = box ? box.querySelector(".call__k").textContent : null;
    swap(node, UI.scale({ kind: node.getAttribute("data-scale"), pos: pos ? Number(pos) : null,
      word: node.getAttribute("data-word"), label: label, size: node.closest(".call") ? "lg" : null }));
  }
  function enhanceStatus(node) {
    var chip = UI.status(node.getAttribute("data-status")), why = node.getAttribute("title");
    if (why) chip.setAttribute("title", why);
    swap(node, chip);
  }
  /* The cell keeps the text the static page printed (thousands separators on money columns, R8);
     RBOTUI.cell would print the served string, so the button text is put back. */
  function enhanceCell(td) {
    var datum = JSON.parse(td.getAttribute("data-datum")), shown = td.textContent;
    while (td.firstChild) td.removeChild(td.firstChild);
    UI.cell(td, datum);
    var b = td.querySelector(".cellref");
    if (b && shown !== b.firstChild.nodeValue) {
      var label = b.getAttribute("aria-label");
      b.firstChild.nodeValue = shown;
      b.setAttribute("aria-label", shown + label.slice(label.lastIndexOf(", ")));
    }
  }
  /* Replace a static figure by the drawn chart (same id, number and origin); its twin table goes with it.
     A chart that cannot be drawn keeps the static figure and is reported to the console (fail-open, logged). */
  function enhanceChart(fig, byId) {
    var entry = byId[fig.getAttribute("data-chart")];
    if (!entry || !entry.data) return;   /* an undrawable chart is already the n/a frame */
    try {
      var host = el("div"), title = fig.querySelector(".chart__title");
      var spec = Object.assign({}, entry.data, { id: fig.id, headingLevel: title ? Number(title.tagName.slice(1)) : 4 });
      var handle = C[entry.kind](host, spec), drawn = host.firstChild;
      drawn.setAttribute("data-origin", fig.getAttribute("data-origin"));
      drawn.setAttribute("data-chart", entry.chart_id);
      swap(fig, drawn);
      charts.push(handle);
      handle.redraw();
    } catch (err) {
      console.error("report.js: chart " + entry.chart_id + " not drawn: " + err.message);
    }
  }
  function enhance() {
    var byId = {};
    run.charts.forEach(function (c) { byId[c.chart_id] = c; });
    all("[data-scale], [data-status], td[data-datum], figure[data-chart]").forEach(function (node) {
      if (node.hasAttribute("data-scale")) enhanceScale(node);
      else if (node.hasAttribute("data-status")) enhanceStatus(node);
      else if (node.tagName === "TD") enhanceCell(node);
      else enhanceChart(node, byId);
    });
  }

  /* Model column toggles: one button per column kind (historical, PF-LTM, Base, Downside) hides that column in every Model table. */
  function modelToggles() {
    var v = VIEWS.model, kinds = [];
    if (!v) return;
    all("th[data-col-kind]", v.el).forEach(function (th) {
      var k = th.getAttribute("data-col-kind");
      if (k && kinds.indexOf(k) < 0) kinds.push(k);
    });
    if (!kinds.length) return;
    var bar = el("div", { class: "coltoggle", role: "group", "aria-label": "Model columns" }, kinds.map(function (k) {
      var b = el("button", { type: "button", class: "btn btn--quiet", "data-toggle-cols": k, "aria-pressed": "true", text: k.replace(/_/g, " ") });
      b.addEventListener("click", function () {
        var on = b.getAttribute("aria-pressed") !== "true";
        b.setAttribute("aria-pressed", String(on));
        all("table.dt", v.el).forEach(function (t) {
          var head = all("th[data-col-kind]", t).filter(function (th) { return th.getAttribute("data-col-kind") === k; });
          head.forEach(function (th) {
            all("tr", t).forEach(function (tr) { if (tr.cells[th.cellIndex]) tr.cells[th.cellIndex].hidden = !on; });
          });
        });
      });
      return b;
    }));
    var header = v.el.querySelector("header");
    header.parentNode.insertBefore(bar, header.nextSibling);
  }

  /* ------------------------------------------------------------ boot (report-a.js:1693, minus every build function) */
  ORDER.forEach(function (id) {
    var v = VIEWS[id], bar = v.el.querySelector(".vbar");
    if (bar) { bar.appendChild(keyButton()); bar.appendChild(viewTools(v)); }
    buildToc(v);
  });
  enhance();
  modelToggles();
  indexSearch();
  buildSearch();
  UI.init(document);
  UI.roving(main);

  menu.addEventListener("click", function () { sheetOpen(menu.getAttribute("aria-expanded") !== "true"); });
  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape" && keyPop && !keyPop.hidden) { closeKey(true); return; }
    if (e.key === "Escape" && menu.getAttribute("aria-expanded") === "true") { sheetOpen(false); menu.focus(); }
  });
  /* a source note [Cn] opens its passport and keeps its anchor; captured so RBOTUI's own click handler
     (which closes a popover on any click outside it) cannot undo the open, and so a second click closes */
  document.addEventListener("click", function (e) {
    var a = e.target.closest ? e.target.closest("a.cite[data-ref]") : null;
    if (!a) return;
    e.preventDefault();
    e.stopPropagation();
    if (a.getAttribute("aria-expanded") === "true") UI.close(false);
    else UI.open(a.getAttribute("data-ref"), a);
  }, true);
  document.addEventListener("click", function (e) {
    if (menu.getAttribute("aria-expanded") === "true" && !e.target.closest("#pane")) sheetOpen(false);
    if (keyPop && !keyPop.hidden && !e.target.closest(".keypop, .vkey")) closeKey(false);
    /* remember where the reader was before an in-page jump, so Back returns there */
    var a = e.target.closest ? e.target.closest('a[href^="#"]') : null;
    if (a && !e.defaultPrevented) scrolls[hashKey()] = window.scrollY;
  }, true);
  sheet.addEventListener("click", function (e) { if (e.target.closest("a")) sheetOpen(false); });
  var skip = document.querySelector(".skip");
  if (skip) skip.addEventListener("click", function (e) { e.preventDefault(); window.scrollTo(0, 0); VIEWS[activeId || "snapshot"].h1.focus(); });
  if ("scrollRestoration" in history) history.scrollRestoration = "manual";
  window.addEventListener("popstate", function () { traversal = true; });
  window.addEventListener("hashchange", function () { route(true); });
  window.addEventListener("scroll", updateSpy, { passive: true });
  document.addEventListener("toggle", updateSpy, true);
  route(false);
  document.documentElement.setAttribute("data-ready", "1");
})();
