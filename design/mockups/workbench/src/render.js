/* WB render: generic components. Panels, dense tables, marks, badges, verdict bar, condition line, markdown. */
(function () {
  'use strict';
  const WB = window.WB;
  const el = WB.el;

  /* ---------- figures: the figure itself is the button ---------- */
  WB.figLabel = function (value, kind, extra) {
    const w = WB.originWord[kind];
    return String(value) + (w ? ', ' + w.toLowerCase() : '') + (extra ? ', ' + extra : '');
  };
  /* A figure button bound to a descriptor. content: Node | string. opts: {kind, cls, rg: {r,c}, label} */
  WB.fig = function (desc, content, opts) {
    const o = opts || {};
    const kind = o.kind || 'none';
    const mk = o.noMark ? null : WB.mark(kind);
    const b = el(
      'button',
      {
        type: 'button',
        class: 'fig fig-' + kind + (o.cls ? ' ' + o.cls : ''),
        'data-ref': WB.ref(desc),
        'aria-label': o.label,
        'data-rg-r': o.rg ? o.rg.r : false,
        'data-rg-c': o.rg ? o.rg.c : false,
      },
      [mk, content instanceof Node ? content : el('span', { class: 'fv' }, content)]
    );
    return b;
  };

  WB.gapChip = function (ids, opts) {
    const o = opts || {};
    const idList = ids || [];
    const label = o.label != null ? o.label : idList.join(' ');
    const reason = o.reason || '';
    const b = el(
      'button',
      {
        type: 'button',
        class: 'gapchip' + (o.cls ? ' ' + o.cls : ''),
        'data-ref': WB.ref(o.desc || { t: 'gap', ids: idList, items: o.items }),
        'aria-label': 'Not available' + (label ? ', ' + label : '') + (reason ? ': ' + reason : ''),
        title: reason || 'Not available',
        'data-rg-r': o.rg ? o.rg.r : false,
        'data-rg-c': o.rg ? o.rg.c : false,
      },
      [WB.icon('emptyset', { size: 12 }), label ? el('span', { class: 'num' }, label) : el('span', null, 'n/a')]
    );
    return b;
  };

  WB.citeChip = function (moduleId, id) {
    const c = WB.citation(moduleId, id);
    const kind = c ? (c.synthetic ? 'synthetic' : 'cited') : 'none';
    return el(
      'button',
      {
        type: 'button',
        class: 'cm cm-' + kind,
        'data-ref': WB.ref({ t: 'cite', module: moduleId, id }),
        'aria-label': 'Citation ' + id + (c ? ', ' + WB.originWord[kind].toLowerCase() + ', ' + c.source : ', not found'),
        title: c ? c.source + ' \u00B7 ' + c.locator : id + ' not found in ' + moduleId,
      },
      [WB.mark(kind) || WB.icon('info', { size: 10 }), el('span', { class: 'num' }, id)]
    );
  };

  /* A run of more than three citations reads as one chip ("C2–C10", or "9 sources" when the ids are not consecutive) whose
     passport lists every source; each source still opens its own passport from there. */
  WB.citeGroup = function (moduleId, ids) {
    const cites = ids.map((id) => WB.citation(moduleId, id) || { id, module: moduleId, missing: true });
    const nums = ids.map((id) => +id.slice(1));
    const consecutive = nums.every((n, i) => i === 0 || n === nums[i - 1] + 1);
    const label = consecutive ? ids[0] + '–' + ids[ids.length - 1] : ids.length + ' sources';
    const allSyn = cites.every((c) => c.synthetic);
    const kind = allSyn ? 'synthetic' : 'cited';
    const chips = cites.map((c) => ({ id: c.id, module: moduleId, label: c.missing ? 'not found in ' + moduleId : (c.source || '') + (c.locator ? ' · ' + c.locator : ''), synthetic: !!c.synthetic, missing: !!c.missing, desc: { t: 'cite', module: moduleId, id: c.id } }));
    const desc = { t: 'note', kind, code: label, title: ids.length + ' sources', sub: WB.moduleName(moduleId) + (/^CP-/.test(moduleId) ? ' (' + moduleId + ')' : ''), cites: chips, note: 'The sentence cites ' + ids.length + ' sources. Each opens its own passport with the file, locator and verbatim excerpt.' + (cites.some((c) => c.synthetic) && !allSyn ? ' Some are synthetic test data.' : '') };
    return el('button', { type: 'button', class: 'cm cm-' + kind + ' cm-group', 'data-ref': WB.ref(desc), 'aria-label': ids.length + ' citations, ' + ids.join(', '), title: ids.join(', ') }, [WB.icon('doc-stack', { size: 11 }), el('span', { class: 'num' }, label)]);
  };

  /* inline text: [C12] tokens (runs grouped), G ids (bare or in parentheses), **bold**, `code`, (calc: ...) */
  const INLINE_RE = /\*\*([^*]+)\*\*|`([^`]+)`|\[(C\d+(?:\s*,\s*C\d+)*)\]|\((calc): |\b(G\d+)\b|\(\s*(G\d+(?:\s*,\s*G\d+)*)\s*\)/g;
  const CITE_NEXT = /^[\s,;]*\[(C\d+(?:\s*,\s*C\d+)*)\]/;
  WB.inline = function (text, moduleId, opts) {
    const o = opts || {};
    const f = document.createDocumentFragment();
    const s = String(text == null ? '' : text);
    let last = 0;
    let m;
    const re = new RegExp(INLINE_RE.source, 'g');
    while ((m = re.exec(s))) {
      if (m.index > last) f.appendChild(WB.text(s.slice(last, m.index)));
      let end = m.index + m[0].length;
      if (m[1] != null) f.appendChild(el('strong', null, m[1]));
      else if (m[2] != null) f.appendChild(el('code', { class: 'ic-code' }, m[2]));
      else if (m[3] != null) {
        // gather the adjacent cite tokens: [C2][C3] [C4, C5] form one run
        const ids = m[3].split(',').map((x) => x.trim());
        let nx;
        while ((nx = CITE_NEXT.exec(s.slice(end)))) {
          nx[1].split(',').forEach((x) => ids.push(x.trim()));
          end += nx[0].length;
        }
        const uniq = Array.from(new Set(ids));
        f.appendChild(el('span', { class: 'cites' }, uniq.length > 3 ? WB.citeGroup(moduleId, uniq) : uniq.map((id) => WB.citeChip(moduleId, id))));
      } else if (m[4] != null) {
        // "(calc: …)" runs to its matching parenthesis (formulas nest them); it becomes a compact calculated chip whose
        // passport and tooltip hold the formula
        let depth = 1;
        let k = end;
        for (; k < s.length && depth > 0; k++) {
          if (s[k] === '(') depth++;
          else if (s[k] === ')') depth--;
        }
        const formula = s.slice(end, depth === 0 ? k - 1 : k).trim();
        end = k;
        f.appendChild(
          el(
            'button',
            { type: 'button', class: 'calc-inline', 'data-ref': WB.ref({ t: 'note', kind: 'calculated', code: 'calc', title: 'Calculation', sub: moduleId ? WB.moduleName(moduleId) : '', fields: [['Formula', formula, true]], note: WB.ORIGIN_NOTE.calculated }), title: 'Calculated: ' + formula, 'aria-label': 'Calculation: ' + formula },
            [WB.mark('calculated'), el('span', null, 'calc')]
          )
        );
      } else if (m[5] != null) {
        f.appendChild(WB.gapChip([m[5]], { label: m[5] }));
      } else if (m[6] != null) {
        // "(G8)" or "(G10, G11)": the chips carry the meaning, the parentheses go
        m[6].split(',').map((x) => x.trim()).forEach((g) => f.appendChild(WB.gapChip([g], { label: g })));
      }
      last = end;
      re.lastIndex = end;
    }
    if (last < s.length) f.appendChild(WB.text(s.slice(last)));
    if (o.text) return f.textContent;
    return f;
  };

  /* markdown: paragraphs, lists, headings, tables, bold */
  WB.md = function (src, opts) {
    const o = opts || {};
    const mod = o.module;
    const root = document.createDocumentFragment();
    const lines = String(src || '').replace(/\r/g, '').split('\n');
    let i = 0;
    const isSep = (l) => /^\s*\|?[\s:\-|]+\|?\s*$/.test(l) && l.includes('-');
    const cells = (l) => l.trim().replace(/^\|/, '').replace(/\|$/, '').split('|').map((c) => c.trim());
    while (i < lines.length) {
      const l = lines[i];
      if (!l.trim()) {
        i++;
        continue;
      }
      let m = /^(#{1,4})\s+(.*)$/.exec(l);
      if (m) {
        root.appendChild(el('h4', { class: 'md-h' }, WB.inline(m[2], mod)));
        i++;
        continue;
      }
      if (l.trim().startsWith('|') && i + 1 < lines.length && isSep(lines[i + 1])) {
        const head = cells(l);
        i += 2;
        const body = [];
        while (i < lines.length && lines[i].trim().startsWith('|')) body.push(cells(lines[i++]));
        root.appendChild(
          el('div', { class: 'tw' }, [
            el('table', { class: 'dt md-t' }, [
              el('thead', null, el('tr', null, head.map((h) => el('th', { scope: 'col' }, WB.inline(h, mod))))),
              el('tbody', null, body.map((r) => el('tr', null, r.map((c) => el('td', null, WB.inline(c, mod)))))),
            ]),
          ])
        );
        continue;
      }
      m = /^\s*([-*]|\d+\.)\s+(.*)$/.exec(l);
      if (m) {
        const ordered = /\d/.test(m[1]);
        const items = [];
        while (i < lines.length) {
          const mm = /^\s*([-*]|\d+\.)\s+(.*)$/.exec(lines[i]);
          if (mm) {
            items.push(mm[2]);
            i++;
          } else if (lines[i].trim() && /^\s{2,}\S/.test(lines[i]) && items.length) {
            items[items.length - 1] += ' ' + lines[i].trim();
            i++;
          } else break;
        }
        root.appendChild(el(ordered ? 'ol' : 'ul', { class: 'md-l' + (ordered ? ' md-ol' : '') }, items.map((t) => el('li', null, WB.inline(t, mod)))));
        continue;
      }
      const para = [];
      while (i < lines.length && lines[i].trim() && !/^(#{1,4})\s+/.test(lines[i]) && !/^\s*([-*]|\d+\.)\s+/.test(lines[i]) && !lines[i].trim().startsWith('|')) para.push(lines[i++].trim());
      root.appendChild(el('p', { class: 'md-p' }, WB.inline(para.join(' '), mod)));
    }
    return root;
  };
  WB.paragraphs = (src) => String(src || '').split(/\n{2,}/).map((p) => p.trim()).filter(Boolean);

  /* ---------- badges, chips, meters ---------- */
  WB.signalBars = function (level) {
    const svg = WB.svg('svg', { width: 14, height: 12, viewBox: '0 0 14 12', class: 'ic bars', 'aria-hidden': 'true' });
    [3, 6, 9].forEach((h, i) => {
      svg.appendChild(WB.svg('rect', { x: 1 + i * 4.5, y: 11 - h, width: 3, height: h, fill: 'currentColor', opacity: i + 1 <= level ? 1 : 0.25 }));
    });
    return svg;
  };
  WB.badge = function (value, col, opts) {
    const o = opts || {};
    const sg = WB.signal(value, col);
    let icon = null;
    if (sg.icon === 'bars') icon = WB.signalBars(sg.ordinal);
    else if (sg.icon) icon = WB.icon(sg.icon, { size: 12, stroke: 1.8 });
    const word = sg.word;
    return el('span', { class: 'badge tone-' + sg.tone + (o.cls ? ' ' + o.cls : '') }, [icon, el('span', { class: 'bw' }, word)]);
  };
  WB.statusChip = function (status, opts) {
    const o = opts || {};
    return el('span', { class: 'chip tone-' + WB.STATUS_TONE[status] + (o.cls ? ' ' + o.cls : '') }, [WB.icon(WB.STATUS_ICON[status], { size: 13, stroke: 1.8 }), el('span', null, WB.STATUS_WORD[status])]);
  };
  WB.tag = function (kind, label) {
    const labels = { illustrative: 'Illustrative', model: 'Model-written', synthetic: 'Synthetic', primary: 'Primary', text: label };
    const m = kind === 'model' ? WB.mark('model', { size: 10 }) : kind === 'synthetic' ? WB.mark('synthetic', { size: 10 }) : null;
    return el('span', { class: 'tag tag-' + kind }, [m, el('span', null, label || labels[kind])]);
  };
  WB.conditionLine = function (text, opts) {
    const o = opts || {};
    return el('div', { class: 'cond' + (o.cls ? ' ' + o.cls : '') }, [WB.icon('status-notrun', { size: 14 }), el('span', null, WB.inline(text, o.module))]);
  };

  /* ---------- panel ---------- */
  WB.panel = function (cfg) {
    const id = cfg.anchor ? 'p-' + WB.cssId(cfg.anchor) : null;
    const bodyId = id ? id + '-body' : 'pb-' + Math.random().toString(36).slice(2, 8);
    const body = el('div', { class: 'p-body', id: bodyId }, cfg.body);
    const collapsible = cfg.collapsible !== false && !cfg.pinned;
    const head = el('header', { class: 'p-head' });
    const left = el('div', { class: 'p-l' });
    const right = el('div', { class: 'p-r' });
    head.append(left, right);
    left.appendChild(el('h2', { class: 'p-title' }, cfg.title));
    if (cfg.fig) left.appendChild(el('span', { class: 'p-fig num' }, cfg.fig));
    if (cfg.code) left.appendChild(el('span', { class: 'p-code num' }, cfg.code));
    for (const t of cfg.tags || []) left.appendChild(t instanceof Node ? t : WB.tag(t.kind, t.label));
    if (cfg.state) left.appendChild(el('span', { class: 'p-state tone-' + (cfg.state.tone || 'neu') }, [cfg.state.icon ? WB.icon(cfg.state.icon, { size: 12, stroke: 1.8 }) : null, cfg.state.word]));
    if (cfg.note) left.appendChild(el('span', { class: 'p-note' }, cfg.note));
    for (const t of cfg.tools || []) right.appendChild(t);
    if (cfg.link) right.appendChild(el('a', { class: 'p-link', href: cfg.link.href }, [cfg.link.label || 'Full analysis', WB.icon('arrow-right', { size: 12, stroke: 1.8 })]));
    const sec = el('section', { class: 'panel' + (cfg.className ? ' ' + cfg.className : ''), id, 'data-pinned': cfg.pinned ? '1' : false, 'data-collapsible': collapsible ? '1' : false, 'aria-label': typeof cfg.title === 'string' ? cfg.title : false }, [head, body]);
    if (collapsible) {
      const btn = el('button', { type: 'button', class: 'p-toggle', 'aria-expanded': 'true', 'aria-controls': bodyId, 'aria-label': 'Collapse ' + (typeof cfg.title === 'string' ? cfg.title : 'panel') }, WB.icon('chevron-up', { size: 12, stroke: 1.8 }));
      const set = (open) => {
        body.hidden = !open;
        btn.setAttribute('aria-expanded', open ? 'true' : 'false');
        btn.replaceChildren(WB.icon(open ? 'chevron-up' : 'chevron-down', { size: 12, stroke: 1.8 }));
        sec.classList.toggle('is-collapsed', !open);
      };
      btn.addEventListener('click', () => set(body.hidden));
      sec._setOpen = set;
      right.appendChild(btn);
      if (cfg.collapsed) set(false);
    }
    return sec;
  };
  WB.collapseAll = function (root, open) {
    for (const p of WB.qsa('.panel[data-collapsible="1"]', root || document)) if (p._setOpen) p._setOpen(open);
  };
  WB.collapseTool = function (root) {
    let open = true;
    const b = el('button', { type: 'button', class: 'btn-s' }, [WB.icon('collapse-all', { size: 12 }), el('span', null, 'Collapse all')]);
    b.addEventListener('click', () => {
      open = !open;
      WB.collapseAll(root(), open);
      b.replaceChildren(WB.icon(open ? 'collapse-all' : 'expand-all', { size: 12 }), el('span', null, open ? 'Collapse all' : 'Expand all'));
    });
    return b;
  };

  /* ---------- dense table ---------- */
  /* tables whose id is a file path read by what they hold */
  const TABLE_TITLES = { 'prior/diff.json': 'Differences from the Prior Case', 'model.metrics': 'Model credit metrics', 'model.summary': 'Model summary', 'model.house': 'House view', 'model.projection_summary': 'Projection summary' };
  WB.tableTitle = function (id) {
    const key = String(id).split('@').pop();
    if (TABLE_TITLES[key]) return TABLE_TITLES[key];
    const last = key.split('.').pop();
    return WB.colLabel(last);
  };
  /* the row's own words, so a humanised id keeps the capitals its text uses ("Las Vegas", "Caesars Digital") */
  function rowContext(table, r, c) {
    return table.rows[r].filter((v, i) => i !== c && typeof v === 'string' && /\s/.test(v)).join(' ');
  }
  function renderCell(table, r, c) {
    const col = WB.columnKinds(table)[c];
    const v = table.rows[r][c];
    const mod = WB.citeModule(table.owner);
    const rg = { r, c };
    const o = WB.cellOrigin(table, r, c);
    if (o.kind === 'gap') {
      const g = WB.cellGap(table, r, c);
      const reason = g.item ? g.item.text : '';
      return { node: WB.gapChip(g.item ? g.item.ids : [], { reason, items: g.item ? [g.item] : g.moduleItems, rg, desc: { t: 'cell', table: table.id, r, c } }), cls: 'c-gap' };
    }
    if (col.kind === 'scale') {
      const sg = WB.signal(v, col.name === 'status' && table.id === 'cp4.covenant_tests' ? col.name : col.name);
      const content = el('span', { class: 'fv' }, WB.badge(v, col.name));
      return { node: WB.fig({ t: 'cell', table: table.id, r, c }, content, { kind: o.kind, rg, label: WB.figLabel(sg.word, o.kind), cls: 'fig-scale' }), cls: 'c-scale' };
    }
    if (col.kind === 'numeric') {
      const shown = WB.fmtNum(v, { group: true });
      return { node: WB.fig({ t: 'cell', table: table.id, r, c }, shown, { kind: o.kind, rg, label: WB.figLabel(shown, o.kind) }), cls: 'c-num' };
    }
    if (col.kind === 'id') {
      if (WB.HUMAN_ID_COLS.test(col.name) && (WB.isSnake(v) || /^[a-z][a-z0-9]*$/.test(String(v)))) return { node: el('span', { class: 'idv hum', title: String(v) }, WB.humanizeId(v, rowContext(table, r, c))), cls: 'c-id' };
      // a source id column holds citation tokens: they open their passports like any other citation
      if (/^\s*\[C\d+/.test(String(v))) return { node: el('span', { class: 'cites' }, WB.inline(String(v), mod)), cls: 'c-id' };
      if (WB.PERIOD_ID.test(String(v))) return { node: el('span', { class: 'num idv', title: String(v) }, WB.periodLabel(v)), cls: 'c-id' };
      if (/(^|_)case(_name)?$/.test(col.name)) return { node: el('span', { class: 'idv hum' }, WB.enumWord(v)), cls: 'c-text' };
      // a claim class reads by name where its table does not name it (recoveries); the register's id stays beside it, small
      if (col.name === 'class_id' && table.columns.indexOf('claim') < 0 && WB.claimName(v) !== String(v)) return { node: el('span', { class: 'idv hum', title: String(v) }, [WB.claimName(v), ' ', el('span', { class: 'num idv-sub' }, String(v))]), cls: 'c-text' };
      // names held in an id column (bond names, KPI labels) read as text; codes stay mono
      if (col.textual) return { node: el('span', { class: 'idv hum' }, String(v)), cls: 'c-text' };
      return { node: el('span', { class: 'num idv' }, String(v)), cls: 'c-id' };
    }
    // text and prose
    const shownText = /^[A-Z][A-Z0-9_]+$/.test(String(v)) ? WB.PATHWAYS[v] || WB.colLabel(String(v)) : WB.humanize(String(v));
    const wrap = el('span', { class: 'txt' }, WB.inline(shownText, mod));
    if (o.kind === 'model') {
      const b = WB.fig({ t: 'note', kind: 'model', code: table.id, title: col.label, sub: WB.moduleName(mod), fields: [['Served as', String(v).slice(0, 220), false]], note: WB.ORIGIN_NOTE.model, table: { id: table.id, row: r, col: c } }, WB.mark('model'), { kind: 'model', noMark: true, cls: 'fig-ghost', rg, label: 'Model-written text, ' + col.label });
      wrap.appendChild(b);
    }
    return { node: wrap, cls: col.kind === 'prose' ? 'c-prose' : 'c-text' };
  }
  WB.renderCell = renderCell;

  function rowSource(table, r, rgc) {
    const info = WB.rowInfo(table, r);
    if (!info) return null;
    if (!info.cites.length && !info.calc) return null;
    const kind = info.calc ? 'calculated' : info.synthetic ? 'synthetic' : 'cited';
    const label = (info.calc ? 'calculated' : kind) + (info.cites.length ? ', ' + info.cites.length + ' source' + (info.cites.length > 1 ? 's' : '') : '');
    return WB.fig({ t: 'row', table: table.id, r }, el('span', { class: 'fv num' }, info.cites.length ? String(info.cites.length) : ''), { kind, cls: 'fig-src', rg: { r, c: rgc }, label: 'Row sources: ' + label });
  }

  /* machine ids a table also names in words: shown only when no name column stands beside them (the passport keeps the id) */
  const NAMED_BY = { facility_id: ['facility', 'instrument'], portfolio_id: ['portfolio_name'] };
  const autoHidden = (table, name) => (NAMED_BY[name] || []).some((n) => table.columns.indexOf(n) >= 0);
  WB.renderTable = function (table, opts) {
    const o = opts || {};
    const kinds = WB.columnKinds(table).filter((k) => k.kind !== 'hidden' && !(o.hide || []).includes(k.name) && !autoHidden(table, k.name));
    const hasCite = table.columns.indexOf('cite') >= 0;
    const maxRows = o.maxRows || 40;
    const unit = WB.tableUnit(table);
    const rowHead = kinds.findIndex((k) => k.kind === 'text' || k.kind === 'id' || k.kind === 'prose');
    const firstIsLabel = rowHead === 0 && kinds.length > 1;
    const srcCol = table.columns.length; // roving grid column for the row-source button
    const thead = el('thead', null, el('tr', null, [
      kinds.map((k) => el('th', { scope: 'col', class: 'h-' + k.kind }, k.label)),
      hasCite ? el('th', { scope: 'col', class: 'h-src' }, el('span', { class: 'sr-only' }, 'Row sources')) : null,
    ]));
    const tbody = el('tbody');
    const build = (n) => {
      const frag = document.createDocumentFragment();
      for (let r = 0; r < Math.min(n, table.rows.length); r++) {
        const tr = el('tr', { 'data-r': r });
        kinds.forEach((k, ki) => {
          const cell = renderCell(table, r, k.index);
          const tag = ki === 0 && firstIsLabel ? 'th' : 'td';
          tr.appendChild(el(tag, { class: cell.cls + (tag === 'th' ? ' c-rowh' : ''), scope: tag === 'th' ? 'row' : false }, cell.node));
        });
        if (hasCite) {
          const src = rowSource(table, r, srcCol);
          tr.appendChild(el('td', { class: 'c-src' }, src));
        }
        frag.appendChild(tr);
      }
      return frag;
    };
    tbody.appendChild(build(maxRows));
    const tbl = el('table', { class: 'dt', 'data-table': table.id, 'data-grid': '1' }, [
      o.caption !== false ? el('caption', { class: 'sr-only' }, (o.caption || WB.tableTitle(table.id)) + (unit ? ', ' + unit : '')) : null,
      thead,
      tbody,
    ]);
    const wrap = el('div', { class: 'tw', id: o.anchor ? 't-' + WB.cssId(o.anchor) : false }, tbl);
    if (!table.rows.length) {
      tbody.appendChild(el('tr', null, el('td', { class: 'c-empty', colspan: kinds.length + (hasCite ? 1 : 0) }, 'This table has no rows in this run.')));
    }
    wrap._expand = () => {
      if (table.rows.length > maxRows && !wrap._expanded) {
        wrap._expanded = true;
        tbody.replaceChildren(build(table.rows.length));
        if (more) more.remove();
        WB.initGrid(tbl);
      }
    };
    let more = null;
    if (table.rows.length > maxRows) {
      more = el('button', { type: 'button', class: 'btn-s more' }, 'Show all ' + table.rows.length + ' rows');
      more.addEventListener('click', () => wrap._expand());
      wrap.appendChild(more);
    }
    WB.initGrid(tbl);
    return wrap;
  };

  /* One table, one tab stop: arrows move between figures. */
  WB.initGrid = function (tbl) {
    // every button or link inside the table joins the grid, positioned by its row and cell
    WB.qsa('button, a[href]', tbl).forEach((b) => {
      const tr = b.closest('tr');
      const td = b.closest('td, th');
      if (!tr || !td) return;
      b.dataset.rgR = String(tr.rowIndex);
      b.dataset.rgC = String(td.cellIndex);
    });
    const btns = WB.qsa('[data-rg-r]', tbl);
    btns.forEach((b, i) => b.setAttribute('tabindex', i === 0 ? '0' : '-1'));
    if (tbl._gridBound) return;
    tbl._gridBound = true;
    tbl.addEventListener('focusin', (e) => {
      const t = e.target.closest('[data-rg-r]');
      if (!t) return;
      WB.qsa('[data-rg-r][tabindex="0"]', tbl).forEach((b) => b.setAttribute('tabindex', '-1'));
      t.setAttribute('tabindex', '0');
    });
    tbl.addEventListener('keydown', (e) => {
      const keys = ['ArrowLeft', 'ArrowRight', 'ArrowUp', 'ArrowDown', 'Home', 'End'];
      if (!keys.includes(e.key)) return;
      const cur = e.target.closest('[data-rg-r]');
      if (!cur) return;
      const all = WB.qsa('[data-rg-r]', tbl);
      const r = +cur.dataset.rgR;
      const c = +cur.dataset.rgC;
      const rowOf = (n) => all.filter((b) => +b.dataset.rgR === n);
      let target = null;
      if (e.key === 'ArrowRight' || e.key === 'ArrowLeft') {
        const row = rowOf(r);
        const idx = row.indexOf(cur);
        target = row[idx + (e.key === 'ArrowRight' ? 1 : -1)] || null;
      } else if (e.key === 'Home' || e.key === 'End') {
        const row = rowOf(r);
        target = e.key === 'Home' ? row[0] : row[row.length - 1];
      } else {
        const rows = Array.from(new Set(all.map((b) => +b.dataset.rgR))).sort((a, b) => a - b);
        const ri = rows.indexOf(r) + (e.key === 'ArrowDown' ? 1 : -1);
        if (ri >= 0 && ri < rows.length) {
          const cand = rowOf(rows[ri]);
          target = cand.reduce((best, b) => (best === null || Math.abs(+b.dataset.rgC - c) < Math.abs(+best.dataset.rgC - c) ? b : best), null);
        }
      }
      if (target) {
        e.preventDefault();
        target.focus();
      }
    });
  };

  /* One tab stop per block of figures outside tables (key findings, call lines, tiles, lists of flags, prose with chips):
     the figures and links inside are one roving group; arrows, Home and End move between them (spec §5, keyboard). */
  const ROVE_ITEMS = 'button, a[href]';
  const visible = (n) => n.getClientRects().length > 0;
  WB.roving = function (box) {
    if (!box || box._rove) return;
    const items = () => WB.qsa(ROVE_ITEMS, box).filter((n) => !n.closest('[data-grid], .wbc') && n.closest('[data-roving]') === box);
    const all = items();
    if (all.length < 2) return;
    box._rove = true;
    box.dataset.roving = '1';
    const settle = (keep) => {
      const list = items();
      const shown = list.filter(visible);
      // a group inside a collapsed panel keeps its first item as the stop, so it is reachable once the panel opens
      const stop = keep && shown.includes(keep) ? keep : shown[0] || list[0];
      list.forEach((n) => n.setAttribute('tabindex', n === stop ? '0' : '-1'));
    };
    settle();
    box.addEventListener('focusin', (e) => {
      const t = e.target.closest(ROVE_ITEMS);
      if (t && items().includes(t)) settle(t);
    });
    box.addEventListener('toggle', () => settle(box.querySelector('[tabindex="0"]')), true);
    box.addEventListener('keydown', (e) => {
      const keys = ['ArrowLeft', 'ArrowRight', 'ArrowUp', 'ArrowDown', 'Home', 'End'];
      if (!keys.includes(e.key)) return;
      const cur = e.target.closest(ROVE_ITEMS);
      const list = items().filter(visible);
      const i = list.indexOf(cur);
      if (i < 0) return;
      const n = e.key === 'Home' ? 0 : e.key === 'End' ? list.length - 1 : i + (e.key === 'ArrowRight' || e.key === 'ArrowDown' ? 1 : -1);
      if (n < 0 || n >= list.length) return;
      e.preventDefault();
      settle(list[n]);
      list[n].focus();
    });
  };
  /* groups a view marks with data-roving, plus the shared blocks of figures the pages compose */
  WB.ROVING_BLOCKS = '[data-roving], .fpa-kf, .fpa-desc, .fpa-cols, .fpa-thesis, .fb-flags, .fb-cards, .fb-cv, .fb-cv-txt, .fb-2col, .fb-note, .fpa-note, .fb-limits, .fb-thesis, .fl-list, .headline, .md, .gap-list, .mv-lim, .lim-l, .fp-recs';
  WB.initRovingIn = function (root) {
    WB.qsa(WB.ROVING_BLOCKS, root).forEach((box) => {
      if (box.parentElement && box.parentElement.closest('[data-roving]')) return;
      box.dataset.roving = '1';
      WB.roving(box);
    });
  };

  /* One-row tables read as key/value lists */
  WB.renderKV = function (table, opts) {
    const o = opts || {};
    const kinds = WB.columnKinds(table).filter((k) => k.kind !== 'hidden' && !(o.hide || []).includes(k.name));
    const r = o.row || 0;
    const tbody = el('tbody');
    kinds.forEach((k, i) => {
      const cell = renderCell(table, r, k.index);
      tbody.appendChild(el('tr', null, [el('th', { scope: 'row', class: 'kv-k' }, k.label), el('td', { class: 'kv-v ' + cell.cls }, cell.node)]));
      const fig = cell.node.matches && cell.node.matches('[data-rg-r]') ? cell.node : null;
      if (fig) {
        fig.dataset.rgR = String(i);
        fig.dataset.rgC = '0';
      }
    });
    const tbl = el('table', { class: 'dt kv', 'data-table': table.id, 'data-grid': '1' }, [el('caption', { class: 'sr-only' }, o.caption || WB.tableTitle(table.id)), tbody]);
    WB.initGrid(tbl);
    return el('div', { class: 'tw' }, tbl);
  };

  /* Panel tags from the table: illustrative scales, synthetic rows, model-written text */
  WB.tableTags = function (table) {
    const kinds = WB.columnKinds(table);
    const tags = [];
    let ill = false;
    let model = false;
    let syn = false;
    for (const k of kinds) {
      if ((k.kind === 'scale' || WB.JUDGEMENT_NUMERIC[table.twinOf || table.id] === k.name) && table.rows.length) {
        const o = WB.cellOrigin(table, 0, k.index);
        if (o.kind === 'illustrative') ill = true;
      }
      if (k.modelWritten && table.rows.length) model = true;
    }
    for (let r = 0; r < table.rows.length && !syn; r++) {
      const info = WB.rowInfo(table, r);
      if (info && info.allSynthetic) syn = true;
    }
    if (ill) tags.push({ kind: 'illustrative', label: 'Illustrative' });
    if (syn) tags.push({ kind: 'synthetic', label: 'Synthetic' });
    if (model) tags.push({ kind: 'model', label: 'Model-written' });
    return tags;
  };

  WB.ownerHref = function (owner) {
    if (!owner || owner === 'RUN_BRIEF') return null;
    if (owner === 'MODEL' && WB.views.model) return WB.href('model');
    if (owner === 'FIT' && WB.views.fit) return WB.href('fit');
    return WB.href('module/' + owner);
  };

  /* A panel for one run table */
  WB.tablePanel = function (tableId, opts) {
    const o = opts || {};
    const table = typeof tableId === 'string' ? WB.table(tableId) : tableId;
    if (!table) {
      return WB.panel({ title: o.title || WB.tableTitle(tableId), anchor: o.anchor || tableId, body: WB.conditionLine('This table is not in this run.'), collapsible: false, className: 'panel-cond' });
    }
    const kv = o.kv != null ? o.kv : table.rows.length === 1 && table.columns.length > 3;
    const unit = WB.tableUnit(table);
    const body = kv ? WB.renderKV(table, o) : WB.renderTable(table, Object.assign({ anchor: table.id }, o));
    const owner = table.owner;
    const status = owner === 'RUN_BRIEF' ? null : WB.stepStatus(owner);
    return WB.panel({
      title: o.title || WB.tableTitle(table.id),
      // opts.code === null hides the owner code (a module view does not repeat its own code on every table)
      code: o.code !== undefined ? o.code : owner === 'RUN_BRIEF' ? 'BRIEF' : owner,
      fig: o.fig,
      tags: o.tags || WB.tableTags(table),
      state: o.state === false ? null : status === 'blocked' ? { word: 'Blocked', tone: 'neg', icon: 'status-blocked' } : null,
      note: o.note !== undefined ? o.note : unit || null,
      anchor: o.anchor || table.id,
      link: o.link === false ? null : o.link || (WB.ownerHref(owner) ? { href: WB.ownerHref(owner) + '/t-' + WB.cssId(table.id), label: 'Full analysis' } : null),
      body,
      collapsed: o.collapsed,
      className: o.className,
    });
  };

  /* ---------- charts: the slot shows each chart's table twin until WB.chart lands ---------- */
  /* A declared n/a chart carries data = { unavailable: 'reason' }. Returns the reason or null. */
  WB.chartUnavailable = function (chart) {
    const d = chart.data || {};
    return typeof d.unavailable === 'string' ? d.unavailable : null;
  };
  /* The twin of a chart's table, as a table in its own right (id "<chart_id>@<table_id>") so every cell resolves to the twin. */
  WB.chartTwinTables = function (chart) {
    const out = [];
    if (WB.chartUnavailable(chart)) return out;
    for (const tid of Object.keys(chart.data || {})) {
      const src = chart.data[tid];
      if (!src || !Array.isArray(src.columns)) continue;
      const key = chart.chart_id + '@' + tid;
      let twin = WB.run._tables.get(key);
      if (!twin) {
        const real = WB.table(tid);
        let cols = src.columns.slice();
        let rows = src.rows.map((r) => r.slice());
        if (real) {
          const ci = real.columns.indexOf('cite');
          if (ci >= 0 && !cols.includes('cite')) {
            // carry the row's cite when the chart row matches a table row on the columns it kept
            const idx = cols.map((c) => real.columns.indexOf(c));
            const cites = rows.map((row) => {
              const hit = real.rows.find((rr) => idx.every((ri, k) => ri >= 0 && rr[ri] === row[k]));
              return hit ? hit[ci] : '\u2014';
            });
            cols = cols.concat('cite');
            rows = rows.map((row, i) => row.concat(cites[i]));
          }
        }
        twin = { id: key, owner: real ? real.owner : 'RUN_BRIEF', columns: cols, rows, twinOf: tid, chartId: chart.chart_id };
        WB.run._tables.set(key, twin);
      }
      out.push(twin);
    }
    return out;
  };
  /* opts.caption === false: the panel or a sub-heading already names the chart, so the caption is for assistive technology only.
     opts.summary: a one-sentence data summary written by the page; the fixture's own summary ("N populated row(s) from …") is never shown. */
  WB.chartSlot = function (chart, opts) {
    const o = opts || {};
    const title = WB.chartTitle(chart.chart_id);
    const fig = el('figure', { class: 'chart-slot', id: 'c-' + WB.cssId(chart.chart_id), 'data-chart': chart.chart_id });
    fig.appendChild(el('figcaption', { class: 'cs-cap' + (o.caption === false ? ' sr-only' : '') }, [el('span', { class: 'cs-title' }, title)]));
    const host = el('div', { class: 'cs-host' });
    fig.appendChild(host);
    const na = WB.chartUnavailable(chart);
    if (na) {
      fig.classList.add('is-na');
      host.appendChild(el('div', { class: 'cs-na' }, [WB.icon('emptyset', { size: 16 }), el('div', null, [el('strong', null, 'Not drawn'), el('p', null, na)])]));
    } else if (typeof WB.chart === 'function') {
      WB.chart(host, Object.assign({}, chart, { summary: o.summary || '' }), o);
    } else {
      const twins = WB.chartTwinTables(chart);
      for (const t of twins) host.appendChild(WB.renderTable(t, { maxRows: 12, caption: title + ': ' + WB.tableTitle(t.id) }));
    }
    return fig;
  };
  /* charts for a Front Page block number, or a module */
  WB.chartsForBlock = function (n) {
    return (WB.run.charts || []).filter((c) => c.where === 'front_page:' + n);
  };
  WB.chartsForModule = function (moduleId) {
    return (WB.run.charts || []).filter((c) => {
      if (c.where === 'analysis:' + moduleId) return true;
      if (c.where !== 'analysis') return false;
      const t = (c.tables || []).map((tid) => WB.tableOwner(tid)).find(Boolean);
      return t === moduleId;
    });
  };

  /* ---------- position tiles and the verdict bar ---------- */
  WB.meter = function (pos, total) {
    const box = el('span', { class: 'meter', 'aria-hidden': 'true' });
    for (let i = 1; i <= total; i++) box.appendChild(el('span', { class: 'mt' + (i === pos ? ' on' : '') }));
    return box;
  };
  /* tile: { label, value, scale, producer, reason, ref, illustrative, honest } */
  WB.tile = function (t) {
    const wrap = el('div', { class: 'tile', 'data-key': t.key || false });
    wrap.appendChild(el('span', { class: 'tile-l' }, t.label));
    if (t.value == null || t.value === '') {
      // the honest state of a tile: "Not produced", a short reason and the module that would produce it; the full reason is its passport
      const reason = t.reason || 'Not produced in this run.';
      const desc = { t: 'note', kind: 'none', code: t.producer || '', title: t.label + ': not produced', sub: t.producer ? 'Would be produced by ' + WB.moduleName(t.producer) + ' (' + t.producer + ')' : '', fields: [['Reason', reason, false]], note: 'A tile the run did not produce reads Not produced, never a placeholder value.' };
      const btn = el('button', { type: 'button', class: 'tile-btn', 'data-ref': WB.ref(desc), 'aria-label': t.label + ': not produced. ' + reason }, [
        el('span', { class: 'tile-row' }, [
          el('span', { class: 'tile-sq np', 'aria-hidden': 'true' }, '\u2013'),
          el('span', { class: 'tile-w' }, [el('span', { class: 'tile-word' }, 'Not produced'), el('span', { class: 'tile-why', title: reason }, t.short || reason)]),
        ]),
      ]);
      wrap.appendChild(btn);
      if (t.producer) wrap.appendChild(el('a', { class: 'tile-mod num', href: WB.href('module/' + t.producer), 'aria-label': 'Open ' + WB.moduleName(t.producer) }, t.producer));
      return wrap;
    }
    const sg = WB.signal(t.value, t.scale === 'dir' ? 'dir' : t.key);
    let sqContent;
    let word = sg.label || sg.word;
    let tone = sg.tone;
    if (t.scale === 'dir') {
      const di = { improving: 'arrow-up', stable: 'arrow-flat', deteriorating: 'arrow-down' }[String(t.value).toLowerCase()] || 'arrow-flat';
      tone = { improving: 'pos', stable: 'neu', deteriorating: 'neg' }[String(t.value).toLowerCase()] || 'neu';
      sqContent = WB.icon(di, { size: 15, stroke: 2.2 });
      word = t.value;
    } else if (t.scale === 'gate') {
      const lc = String(t.value).toLowerCase();
      tone = lc === 'met' ? 'neg' : lc === 'not met' ? 'pos' : 'cau';
      sqContent = WB.icon('gauge', { size: 15, stroke: 1.8 });
      word = t.value;
    } else if (t.scale === 'outlook') {
      tone = { positive: 'pos', neutral: 'neu', negative: 'neg' }[String(t.value).toLowerCase()] || 'neu';
      sqContent = WB.icon({ positive: 'arrow-up', neutral: 'arrow-flat', negative: 'arrow-down' }[String(t.value).toLowerCase()] || 'arrow-flat', { size: 15, stroke: 2.2 });
      word = t.value;
    } else if (t.scale === 'plain') {
      tone = t.tone || sg.tone;
      sqContent = sg.icon && sg.icon !== 'bars' ? WB.icon(sg.icon, { size: 15, stroke: 2 }) : WB.icon('info', { size: 15, stroke: 1.8 });
      word = t.value;
    } else if (t.scale === 'cov') {
      tone = sg.tone;
      sqContent = sg.icon ? WB.icon(sg.icon, { size: 15, stroke: 2 }) : null;
      word = t.value;
    } else if (t.scale === 'press') {
      tone = sg.tone;
      sqContent = sg.icon === 'bars' ? WB.signalBars(sg.ordinal) : null;
      word = t.value;
    } else if (t.scale === 'five') {
      tone = +t.value <= 2 ? 'neg' : +t.value === 3 ? 'cau' : 'pos';
      sqContent = el('span', { class: 'num' }, t.value);
      word = t.word || t.value + ' of 5';
    } else {
      sqContent = el('span', { class: 'num' }, sg.pos || sg.word.slice(0, 2));
    }
    const sq = el('span', { class: 'tile-sq tone-' + tone + (t.illustrative ? ' ill' : '') }, sqContent);
    const wordBox = el('span', { class: 'tile-w' }, [el('span', { class: 'tile-word' }, word), t.sub ? el('span', { class: 'tile-sub' }, t.sub) : null, sg.scalePos ? WB.meter(sg.scalePos, 5) : t.scale === 'five' ? WB.meter(+t.value, 5) : null]);
    const inner = el('span', { class: 'tile-row' }, [sq, wordBox]);
    if (t.ref) {
      const b = el('button', { type: 'button', class: 'tile-btn', 'data-ref': WB.ref(t.ref), 'aria-label': t.label + ': ' + (sg.word || t.value) + (t.illustrative ? ', illustrative' : '') }, inner);
      wrap.appendChild(b);
    } else wrap.appendChild(inner);
    return wrap;
  };

  /* The byline in parts: analyst, a quiet "Design fixture" tag for a test run, the date; extra parts (e.g. "Fictional issuer") lead. */
  WB.bylineNodes = function (meta, lead) {
    const parts = [];
    (lead || []).forEach((x) => x && parts.push(el('span', null, x)));
    if (meta.analystName) parts.push(el('span', null, [meta.analystName, meta.designFixture ? el('span', { class: 'v-fix', title: 'Every test run is a design fixture' }, 'Design fixture') : null]));
    if (meta.asOf) parts.push(el('span', null, WB.fmtDate(meta.asOf)));
    return parts.flatMap((p, i) => (i ? [el('span', { class: 'v-dot', 'aria-hidden': 'true' }, '·'), p] : [p]));
  };

  /* Call lines: at most `max` show; the rest sit behind one disclosure that names them. `order` lists labels by priority.
     Idempotent: a page that adds or removes lines after the bar is built calls it again. */
  WB.capCallLines = function (container, opts) {
    if (!container) return;
    const o = opts || {};
    const max = o.max || +container.dataset.max || 3;
    const order = o.order || (container.dataset.order ? container.dataset.order.split('|') : []);
    container.dataset.max = String(max);
    if (order.length) container.dataset.order = order.join('|');
    const lines = WB.qsa('.v-line', container);
    const label = (p) => (p.querySelector('.v-ll') ? p.querySelector('.v-ll').textContent.trim() : '');
    const rank = (p) => {
      const i = order.indexOf(label(p));
      return i < 0 ? order.length + lines.indexOf(p) / 100 : i;
    };
    const sorted = lines.slice().sort((a, b) => rank(a) - rank(b));
    const shown = sorted.slice(0, max);
    const rest = sorted.slice(max);
    const kids = shown.slice();
    if (rest.length) {
      const sum = el('summary', { class: 'v-more-s' }, [WB.icon('chevron-down', { size: 11, stroke: 1.8 }), el('span', null, rest.length + ' more: '), el('span', { class: 'v-more-l' }, rest.map(label).join(' · '))]);
      kids.push(el('details', { class: 'v-more' }, [sum].concat(rest)));
    }
    container.replaceChildren(...kids);
  };

  /* cfg: { title, question, illustrative, byline (string) | bylineNodes, tiles:[tile], lines:[{label, tone, children}], honest, tools, maxLines, order } */
  WB.verdictBar = function (cfg) {
    const bar = el('section', { class: 'verdict on-navy', 'aria-label': 'The call' + (cfg.title ? ': ' + cfg.title : '') });
    // row 1: what the page is and the question it answers; row 2: its standing (illustrative, analyst, date, honest state) and tools
    bar.appendChild(el('div', { class: 'v-head' }, [el('h1', { class: 'v-title' }, cfg.title), cfg.question ? el('span', { class: 'v-q' }, cfg.question) : null, cfg.tools || null]));
    bar.appendChild(
      el('div', { class: 'v-meta' }, [
        cfg.illustrative ? el('span', { class: 'v-tag' }, 'ILLUSTRATIVE') : null,
        cfg.bylineNodes ? el('span', { class: 'v-by' }, cfg.bylineNodes) : cfg.byline ? el('span', { class: 'v-by' }, cfg.byline) : null,
        cfg.honest ? el('span', { class: 'v-honest' }, [WB.icon('info', { size: 12, stroke: 1.8 }), cfg.honest]) : null,
      ])
    );
    if (cfg.tiles && cfg.tiles.length) bar.appendChild(el('div', { class: 'v-tiles', 'data-roving': '1', role: 'group', 'aria-label': 'Position tiles' }, cfg.tiles.map((t) => (t.rowBreak ? el('span', { class: 'v-tile-break', 'aria-hidden': 'true' }) : WB.tile(t)))));
    const out = document.createDocumentFragment();
    out.appendChild(bar);
    // the call lines scroll away; the head and the tiles stay pinned
    if (cfg.lines && cfg.lines.length) {
      const box = el(
        'div',
        { class: 'verdict-lines on-navy', 'data-roving': '1' },
        cfg.lines.map((l) => el('p', { class: 'v-line' }, [el('span', { class: 'v-ll tone-' + (l.tone || 'neu') }, l.label), ' ', l.children]))
      );
      WB.capCallLines(box, { max: cfg.maxLines || 3, order: cfg.order || [] });
      out.appendChild(box);
    }
    return out;
  };

  /* ---------- helpers views share ---------- */
  WB.figNumber = function (prefix, n) {
    return 'Fig. ' + prefix + '.' + n;
  };
  WB.scrollToAnchor = function (anchor) {
    if (!anchor) return false;
    const canvas = document.getElementById('canvas');
    const node = document.getElementById(anchor) || document.getElementById('p-' + anchor) || document.getElementById('t-' + anchor) || document.getElementById('c-' + anchor);
    if (!node || !canvas) return false;
    const top = node.getBoundingClientRect().top - canvas.getBoundingClientRect().top + canvas.scrollTop - 8;
    canvas.scrollTo({ top: Math.max(0, top) });
    node.classList.add('is-target');
    setTimeout(() => node.classList.remove('is-target'), 1600);
    return true;
  };
})();
