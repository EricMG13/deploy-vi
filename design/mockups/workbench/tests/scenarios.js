/* Interaction scenarios for the Workbench, driven from a same-origin harness page (headless Chrome, check.py --interact).
   Test code only: it is not part of dist/. Each check pushes [name, pass, detail]. */
(async function () {
  const results = [];
  const check = (name, pass, detail) => results.push([name, !!pass, detail === undefined ? '' : String(detail)]);
  const frame = document.getElementById('f');
  const BASE = '/design/mockups/workbench/dist/rbot-workbench.html';
  const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
  async function until(fn, ms = 6000) {
    const t0 = Date.now();
    while (Date.now() - t0 < ms) {
      try {
        const v = fn();
        if (v) return v;
      } catch (e) { /* keep polling */ }
      await sleep(25);
    }
    return null;
  }
  async function open(hash, size) {
    if (size) {
      frame.style.width = size[0] + 'px';
      frame.style.height = size[1] + 'px';
    }
    frame.src = 'about:blank';
    await sleep(20);
    frame.src = BASE + hash;
    const ok = await until(() => frame.contentDocument && frame.contentDocument.documentElement.dataset.ready === '1' && frame.contentWindow.WB && frame.contentDocument.location.hash === hash.replace(/^$/, frame.contentDocument.location.hash), 20000);
    return ok ? frame.contentWindow : null;
  }
  const $ = (sel, w) => (w || frame.contentWindow).document.querySelector(sel);
  const $$ = (sel, w) => Array.from((w || frame.contentWindow).document.querySelectorAll(sel));
  const key = (w, el, k, opts) => el.dispatchEvent(new w.KeyboardEvent('keydown', Object.assign({ key: k, bubbles: true, cancelable: true }, opts || {})));
  const text = (sel, w) => (($(sel, w) || {}).textContent || '').trim();

  try {
    /* ---- passports ---- */
    let w = await open('#/czr-full-credit-assessment/module/CP-1B');
    check('open module CP-1B', w && w.document.documentElement.dataset.errors === '0');
    const cited = $$('.dt[data-table="cp1b.period_comparison"] .fig-cited')[0];
    check('cited figure present', cited);
    if (cited) {
      cited.focus();
      cited.click();
      check('cited: passport opens', await until(() => $('.pp-title')));
      check('cited: kind word', /CITED/.test(text('.pp-kind')), text('.pp-kind'));
      check('cited: verbatim excerpt', $('.pp-ex') && $('.pp-ex').textContent.length > 5, $('.pp-ex') && $('.pp-ex').textContent.slice(0, 60));
      check('cited: file field', /Earnings_Release|10Q|10K|\.txt/.test(text('.pp-f')), text('.pp-f').slice(0, 80));
      check('cited: focus on inspector heading', w.document.activeElement === $('.pp-title'), w.document.activeElement && w.document.activeElement.className);
      check('cited: figure marked selected', cited.classList.contains('is-selected'));
      key(w, w.document.activeElement, 'Escape');
      check('cited: Escape returns focus to the figure', w.document.activeElement === cited, w.document.activeElement && w.document.activeElement.className);
    }
    const calcCells = $$('.dt[data-table="cp1b.period_comparison"] tbody tr:first-child .fig-calculated');
    check('calculated figures present (abs change, pct change)', calcCells.length >= 2, calcCells.length);
    if (calcCells.length >= 2) {
      calcCells[0].click();
      await sleep(60);
      check('formula: Abs change does not borrow the percentage formula', !$('.pp-formula') && /Abs change/i.test(text('.pp-title')), text('.pp-title') + ' / ' + text('.pp-f').slice(0, 60));
      check('formula: the row formula is still shown for reference', /percentage change/.test(text('.pp-note')), text('.pp-note').slice(0, 80));
      calcCells[1].click();
      await until(() => $('.pp-formula'));
      check('formula: % change shows its own formula', /2993/.test(text('.pp-formula')), text('.pp-formula'));
      const chips = $$('.pp-chips .pchip');
      check('calculated: input chips are labelled with id and label', chips.length >= 2 && chips.every((c) => c.querySelector('.pc-id') && c.querySelector('.pc-l').textContent.length > 3), chips.map((c) => c.textContent.slice(0, 40)).join(' | '));
      if (chips[0]) {
        chips[0].click();
        await sleep(50);
        check('calculated: input chip opens its own passport with Back', $('.pp-back') && $('.pp-title'), text('.pp-title'));
        $('.pp-back').click();
        await sleep(50);
        check('calculated: Back returns to the calculation', /2993/.test(text('.pp-formula')));
      }
    }
    check('labels: metric ids are humanised, never raw snake_case', !/net_revenues_q2/.test(text('.dt[data-table="cp1b.period_comparison"]')) && /Net revenues, Q2/.test(text('.dt[data-table="cp1b.period_comparison"]')) && /Adjusted EBITDA, H1/.test(text('.dt[data-table="cp1b.period_comparison"]')), text('.dt[data-table="cp1b.period_comparison"] tbody tr').slice(0, 50));
    check('no fixture or dev text on screen', !/populated row|not drawn yet|design fixture/i.test(text('#canvas') + text('#navigator')), '');
    // gap chip
    const gap = $$('.gapchip')[0];
    if (gap) {
      gap.click();
      await sleep(50);
      check('gap: passport', /N\/A/i.test(text('.pp-kind')) && $('.pp-f').textContent.length > 10, text('.pp-kind') + ' ' + text('.pp-f').slice(0, 80));
    } else check('gap chip present on CP-1B', false);
    // Table and Gaps tabs
    const cellForTable = $$('.dt[data-table="cp1b.kpi_changes"] .fig-cited')[0];
    if (cellForTable) {
      cellForTable.click();
      await sleep(50);
      $('#it-table').click();
      await sleep(80);
      check('Table tab: table twin with highlighted row', $('.ti .dt tr.hl'), $$('.ti .dt tr.hl').length);
      $('#it-gaps').click();
      await sleep(50);
      check('Gaps tab: lists the page gaps', $$('.pp-gaps li').length >= 3, $$('.pp-gaps li').length);
    }

    /* ---- synthetic and illustrative on the Front Page ---- */
    w = await open('#/czr-full-credit-assessment/front');
    const syn = $$('.fig-synthetic')[0];
    check('synthetic figure on the Front Page', syn);
    if (syn) {
      syn.click();
      await sleep(60);
      check('synthetic: TEST DATA rationale', /SYNTHETIC/.test(text('.pp-kind')) && /synthetic|plausible|illustrate|invented|analyst supplies/i.test(text('.pp-ex')), text('.pp-kind') + ' ' + text('.pp-ex').slice(0, 80));
    }
    const ill = $$('.fig-illustrative')[0];
    check('illustrative scale figure', ill);
    if (ill) {
      ill.click();
      await sleep(60);
      check('illustrative: passport', /ILLUSTRATIVE/.test(text('.pp-kind')), text('.pp-kind'));
    }
    const tile = $('.tile-btn');
    if (tile) {
      tile.click();
      await sleep(60);
      check('verdict tile opens a passport', $('.pp-title'), text('.pp-title'));
    }

    /* ---- the honest state ---- */
    w = await open('#/czr-full-credit-assessment/front');
    const before = $$('.tile-sq.np').length;
    $('.nav-issuer').click();
    await until(() => $('.rs-switch'));
    check('run switcher lists eight runs', $$('.rs-row').length === 8, $$('.rs-row').length);
    check('run switcher groups by Pathway', $$('.rs-g').length === 6, $$('.rs-g').length);
    $('.rs-switch').click();
    await sleep(300);
    const after = $$('.tile-sq.np').length;
    check('honest state: Not produced tiles appear', before === 0 && after >= 4, before + ' -> ' + after);
    check('honest state: reason and producing module named', $$('.tile-why .tile-mod').length >= 4, text('.tile-why'));
    key(w, $('.rs-switch') || w.document.body, 'Escape');
    await sleep(50);
    check('Escape closes the run switcher', !$('.rs'));
    $('.nav-issuer').click();
    await until(() => $('.rs-switch'));
    $('.rs-switch').click();
    key(w, w.document.body, 'Escape');
    await sleep(100);

    /* ---- router edge cases ---- */
    w = await open('#/nope/front');
    check('router: unknown run', /Run not found/.test(text('h1')), text('h1'));
    w = await open('#/czr-full-credit-assessment/zzz');
    check('router: unknown view', /View not found/.test(text('h1')), text('h1'));
    w = await open('#/czr-full-credit-assessment/module/CP-ZZ');
    check('router: unknown module', /Module not found/.test(text('h1')), text('h1'));
    w = await open('#/czr-earnings-update/module/CP-3');
    check('router: module absent from this run', /Module not found/.test(text('h1')), text('h1'));
    w = await open('#/czr-full-credit-assessment/module/CP-8');
    check('router: not-run module renders its state', /Not run/.test(text('.chip')) && $('.cond'), text('.chip'));
    w = await open('#/czr-full-credit-assessment/fit');
    check('router: unbuilt view says so, rail item disabled', /not built|not in this/i.test(text('.state-body')) && $('.rail-btn.is-disabled'), text('.state-body'));
    w = await open('#/czr-full-credit-assessment/module/CP-1B/t-cp1b-kpi_changes');
    await sleep(200);
    check('router: anchor scrolls to the table', $('#canvas').scrollTop > 100, $('#canvas').scrollTop);
    check('router: anchor marks its target', $('.is-target'));
    const h1 = text('h1');
    w.location.hash = '#/czr-full-credit-assessment/limitations';
    await until(() => text('h1') === 'Limitations');
    w.history.back();
    await until(() => text('h1') === h1);
    check('router: Back returns to the module', text('h1') === h1, text('h1'));
    w.history.forward();
    await until(() => text('h1') === 'Limitations');
    check('router: Forward returns to Limitations', text('h1') === 'Limitations', text('h1'));
    w = await open('#/czr-full-credit-assessment/evidence/ev-CP-1B-C25');
    await sleep(200);
    check('router: evidence deep link renders its row', $('#ev-CP-1B-C25'), $$('.ev-row').length);
    w = await open('#/larchmere-distressed-restructuring/module/CP-2H');
    check('blocked module: chip', /Blocked/.test(text('.chip')), text('.chip'));
    check('blocked module: still renders its tables', $$('.panel .dt').length >= 1, $$('.panel .dt').length);

    w = await open('#/czr-full-credit-assessment/module');
    check('router: module without an id opens the first plan step', /Source readiness/.test(text('h1')), text('h1'));
    w = await open('#/czr-full-credit-assessment/module/CP-1B/');
    check('router: trailing slash is ignored', /Earnings delta/.test(text('h1')), text('h1'));
    w = await open('#/czr-full-credit-assessment');
    check('router: run without a view opens the Front Page', /Credit Snapshot/.test(text('h1')), text('h1'));
    w = await open('#/czr-full-credit-assessment/front/no-such-anchor');
    check('router: unknown anchor renders without error', w.document.documentElement.dataset.errors === '0' && /Credit Snapshot/.test(text('h1')));
    w = await open('#/czr-full-credit-assessment/module/CP-1B');
    const f1 = $$('.dt[data-table="cp1b.period_comparison"] tbody tr:first-child .fig-calculated')[0];
    f1.focus();
    f1.click();
    await sleep(60);
    $$('.pp-chips .pchip')[0].click();
    await sleep(60);
    key(w, w.document.activeElement, 'Escape');
    check('focus: Escape from a chip opened inside the inspector returns to the original figure', w.document.activeElement === f1, w.document.activeElement && w.document.activeElement.className);
    w.document.querySelector('#it-table').click();
    await sleep(40);
    key(w, w.document.activeElement, 'Escape');
    check('focus: Escape from the Table tab returns to the figure', w.document.activeElement === f1);
    w.location.hash = '#/czr-full-credit-assessment/limitations';
    await until(() => text('h1') === 'Limitations');
    check('focus: inspector clears when the route changes', /Select a figure/.test(text('.insp-body')), text('.insp-body').slice(0, 40));
    check('focus: a route change moves focus to the canvas', w.document.activeElement === $('#canvas'), w.document.activeElement && w.document.activeElement.tagName);

    /* ---- keyboard: one tab stop per table, arrows inside ---- */
    w = await open('#/czr-full-credit-assessment/module/CP-1B');
    const tbl = $('.dt[data-table="cp1b.period_comparison"]');
    const stops = Array.from(tbl.querySelectorAll('[data-rg-r]')).filter((b) => b.getAttribute('tabindex') === '0');
    check('keyboard: one tab stop per table', stops.length === 1, stops.length);
    const first = stops[0];
    first.focus();
    key(w, first, 'ArrowRight');
    const moved = w.document.activeElement;
    check('keyboard: ArrowRight moves within the row', moved !== first && moved.dataset.rgR === first.dataset.rgR, moved.dataset.rgC);
    key(w, moved, 'ArrowDown');
    check('keyboard: ArrowDown moves to the next row', w.document.activeElement.dataset.rgR === String(+first.dataset.rgR + 1), w.document.activeElement.dataset.rgR);
    const nowStops = Array.from(tbl.querySelectorAll('[data-rg-r]')).filter((b) => b.getAttribute('tabindex') === '0');
    check('keyboard: roving tab stop follows focus', nowStops.length === 1 && nowStops[0] === w.document.activeElement);
    w = await open('#/czr-full-credit-assessment/module/CP-4');
    const tabbables = $$('.dt[data-grid]').map((t) => Array.from(t.querySelectorAll('button, a[href]')).filter((b) => b.getAttribute('tabindex') === '0').length);
    check('keyboard: every table (including cite chips inside text) is one tab stop', tabbables.length >= 6 && tabbables.every((n) => n <= 1), tabbables.join(','));
    w = await open('#/czr-full-credit-assessment/module/CP-1B');
    // tab order: rail, navigator, canvas, inspector
    const order = Array.from(w.document.querySelectorAll('#app > *')).map((n) => n.className.split(' ')[0] || n.id).filter(Boolean);
    check('keyboard: DOM order rail, navigator, canvas, inspector', order.slice(1, 5).join(',') === 'rail,navigator,canvas,inspector', order.join(','));

    /* ---- search and switcher ---- */
    key(w, w.document.body, '/');
    await until(() => $('.sq-in'));
    check('search: / opens the switcher with focus in the box', w.document.activeElement === $('.sq-in'));
    const input = $('.sq-in');
    input.value = 'liq';
    input.dispatchEvent(new w.Event('input', { bubbles: true }));
    await sleep(50);
    check('search: results for "liq"', $$('.sq-r').length >= 2 && /Liquidity bridge/.test($('.sq-r').textContent), $$('.sq-r').length);
    key(w, input, 'Enter');
    await sleep(300);
    check('search: Enter navigates to the top module', /module\/CP-2D/.test(w.location.hash), w.location.hash);
    check('search: layer closed after Enter', !$('.sq'));
    key(w, w.document.body, '?');
    await until(() => $('.hk'));
    check('help: ? opens How to read a figure', $('.hk') && /Cited/.test($('.hk').textContent));
    key(w, w.document.activeElement, 'Escape');
    await sleep(50);
    check('help: Escape closes it', !$('.hk'));

    /* ---- navigator ---- */
    w = await open('#/czr-full-credit-assessment/front');
    const nChips = $$('.nchip');
    check('navigator: four filter chips with counts', nChips.length === 4 && nChips.every((c) => /\d/.test(c.textContent)), nChips.map((c) => c.textContent).join(' '));
    $$('.nchip')[1].click();
    await sleep(100);
    const rows = $$('.nav-row');
    const passN = +$$('.nchip')[1].querySelector('.num').textContent;
    check('navigator: chips read in full with count', /With limitations\s*\d+/.test(text('.nav-chips')) && /Pass\s*\d+/.test(text('.nav-chips')) && /Blocked\s*\d+/.test(text('.nav-chips')), text('.nav-chips'));
    check('navigator: With limitations filter shows only those modules', rows.length === passN && rows.length >= 1, rows.length + ' of ' + passN);
    check('navigator: Analysis lists modules only (no host steps)', !/Financial model|Projection|Portfolio Fit/.test(text('.nav-modules')) && /Analysis · 21/.test(text('.nav-group-h')), text('.nav-group-h'));
    check('navigator: On this page lists sections', $$('.ol-i').length >= 10, $$('.ol-i').length);
    w = await open('#/czr-full-credit-assessment/front', [1280, 800]);
    check('1280: navigator starts closed', $('#app').dataset.nav === 'closed' && $('.navigator').getBoundingClientRect().width === 0);
    check('1280: rail, canvas and inspector all have width', $('.rail').getBoundingClientRect().width === 56 && $('#canvas').getBoundingClientRect().width > 800 && $('#inspector').getBoundingClientRect().width === 300, $('#canvas').getBoundingClientRect().width);
    $('.rail-act-g .rail-btn:last-child').click();
    await sleep(50);
    check('1280: rail toggle opens the navigator', $('#app').dataset.nav === 'open' && $('.navigator').getBoundingClientRect().width === 240);
    w = await open('#/czr-full-credit-assessment/front', [1440, 900]);
    check('1440: navigator starts open', $('#app').dataset.nav === 'open');

    /* ---- scroll spy ---- */
    w = await open('#/czr-full-credit-assessment/front');
    const firstOn = text('.ol-i.on');
    const target = $$('.ol-i')[6];
    const node = w.document.getElementById(target.dataset.ol);
    $('#canvas').scrollTop = node.offsetTop - 60;
    $('#canvas').dispatchEvent(new w.Event('scroll'));
    await sleep(100);
    check('scroll spy: outline follows the canvas', text('.ol-i.on') !== firstOn && $$('.ol-i.on').length === 1, firstOn + ' -> ' + text('.ol-i.on'));
    $$('.ol-i')[3].click();
    await sleep(300);
    check('outline link scrolls to its panel and keeps the route', $('#canvas').scrollTop > 100 && /czr-full-credit-assessment\/front\//.test(w.location.hash), w.location.hash);

    /* ---- print ---- */
    w = await open('#/czr-full-credit-assessment/module/CP-1B');
    $$('.p-toggle')[1].click();
    check('print: a panel is collapsed first', $$('.panel.is-collapsed').length === 1);
    w.WB.beforePrint();
    check('print: collapsed panels expand', $$('.panel.is-collapsed').length === 0);
    check('print: endnotes section built', $('#endnotes') && $$('#endnotes li').length >= 5, $$('#endnotes li').length);
    check('print: figures carry endnote numbers', $$('[data-endnote]').length >= 5, $$('[data-endnote]').length);
    w.WB.afterPrint();
    check('print: afterPrint removes endnotes and restores panels', !$('#endnotes') && $$('[data-endnote]').length === 0 && $$('.panel.is-collapsed').length === 1);
  } catch (e) {
    check('scenario threw', false, e && e.stack ? e.stack.split('\n').slice(0, 3).join(' / ') : e);
  }
  const bad = results.filter((r) => !r[1]).length;
  document.getElementById('out').textContent = JSON.stringify({ total: results.length, failed: bad, results });
  document.documentElement.dataset.done = '1';
})();
