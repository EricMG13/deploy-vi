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
    // fixture summaries, the analyst's parenthetical and raw table ids stay off the page (ids live in passports, small, at the foot)
    const shownText = text('#canvas') + text('#navigator');
    const devHit = /populated row|not drawn yet|\(design fixture\)|\b(?:cp\d\w*|snapshot|model|fit)\.[a-z_]{3,}/i.exec(shownText);
    check('no fixture or dev text on screen', !devHit, devHit ? devHit[0] : '');
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
      // the passport of a synthetic figure: kind SYNTHETIC, its file is TEST DATA, and the excerpt is headed as the TEST DATA rationale
      const heads = $$('.pp-h').map((h) => h.textContent);
      check('synthetic: TEST DATA rationale', /SYNTHETIC/.test(text('.pp-kind')) && /TEST DATA/.test(text('.pp-f')) && heads.includes('TEST DATA rationale') && text('.pp-ex').length > 20, text('.pp-kind') + ' | ' + text('.pp-f').slice(0, 60) + ' | ' + heads.join(','));
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
    check('honest state: reason and producing module named', $$('.tile .tile-why').length >= 4 && $$('.tile .tile-mod').length >= 4, text('.tile-why'));
    check('honest state: a Not produced tile opens its reason as a passport', (() => { const b = $$('.tile .tile-btn').find((x) => /not produced/i.test(x.getAttribute('aria-label') || '')); if (!b) return false; b.click(); return /not produced/i.test(text('.pp-title')) && /Reason/.test(text('.pp-f')); })(), text('.pp-title'));
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
    // Portfolio Fit is built; a Pathway that attaches no portfolio shows it as absent with its reason, and the rail item is disabled
    w = await open('#/czr-earnings-update/fit');
    check('router: an unavailable view says why, rail item disabled', /not in this pathway/i.test(text('.state-body')) && $('.rail-btn.is-disabled[aria-label^="Portfolio Fit"]'), text('.state-body'));
    w = await open('#/czr-full-credit-assessment/module/CP-1B/t-cp1b-kpi_changes');
    // the scroll happens in the frame after the route renders: wait for it rather than a fixed 200 ms (a fixed wait was flaky)
    await until(() => $('#canvas').scrollTop > 100, 3000);
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
    check('1280: rail, canvas and the inspector strip all have width (the empty inspector is a strip below 1360px)', $('.rail').getBoundingClientRect().width === 56 && $('#canvas').getBoundingClientRect().width > 1100 && $('#inspector').getBoundingClientRect().width > 0 && $('#inspector').getBoundingClientRect().width < 80, $('#canvas').getBoundingClientRect().width);
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

    /* ---- W6 polish: the call, words for ids, one state per limit ---- */
    w = await open('#/czr-earnings-update/front');
    const visibleLines = $$('.verdict-lines > .v-line').map((l) => l.querySelector('.v-ll').textContent);
    check('call: at most three call lines show, in the content doc order', visibleLines.length === 3 && visibleLines[0] === 'THE QUARTER' && visibleLines[2] === 'NO RECOMMENDATION', visibleLines.join(','));
    check('call: the other lines sit behind one disclosure that names them (the main risk never folds, Watch does)', $('.verdict-lines details.v-more') && /WATCH/.test(text('.v-more-s')) && !/MAIN RISK/.test(text('.v-more-s')), text('.v-more-s'));
    check('call: Earnings Update has no Recommendation tile (content doc 02 states it as a line)', !$$('.tile-l').some((t) => /^Recommendation$/i.test(t.textContent)), $$('.tile-l').map((t) => t.textContent).join(','));
    const barH = $('.verdict').getBoundingClientRect().height + ($('.verdict-lines') ? $('.verdict-lines').getBoundingClientRect().height : 0);
    check('call: the bar leaves the first key panel in the first viewport (1440x900)', barH < 330 && $('#p-fp-headline').getBoundingClientRect().top < 360, Math.round(barH));
    check('byline: analyst with a quiet Design fixture tag, no parenthetical', /Credit Research/.test(text('.v-by')) && $('.v-by .v-fix') && !/\(design fixture\)/i.test(text('.verdict')), text('.v-by'));
    w = await open('#/larchmere-distressed-restructuring/front');
    check('fulcrum line names classes, not claim-class ids', /First-lien claims/.test(text('.verdict-lines')) && !/C\d-[A-Z0-9]+/.test(text('.verdict-lines')), text('.verdict-lines').slice(0, 120));
    check('pinch point: a floor carries its unit', /US\$50m covenant floor/.test(text('#p-runway')), text('#p-runway .fb-note').slice(0, 100));
    check('what changed title fills its date placeholder', !/⟨/.test(text('#canvas') + text('#navigator')));
    w = await open('#/czr-covenant-refinancing/front');
    check('protection scores read as illustrative judgements', $$('#p-protection .fig-illustrative').length >= 5 && $$('#p-protection .fig-cited').length === 0, $$('#p-protection .fig-illustrative').length);
    w = await open('#/czr-full-credit-assessment/front');
    const outstanding = $$('.dt[data-table="snapshot.capital_structure"] tbody tr').map((tr) => tr.textContent);
    check('amounts that look like years are grouped (2,018 not 2018)', outstanding.some((t) => /2,018/.test(t)) && !outstanding.some((t) => /\b2018\b/.test(t) && !/2018-/.test(t)), outstanding.find((t) => /CEI Term Loan B\b/.test(t)));
    const kfStops = $$('.fpa-kf button, .fpa-kf a[href]').filter((b) => b.getAttribute('tabindex') === '0').length;
    check('keyboard: key findings are one tab stop, arrows inside', kfStops === 1, kfStops);
    w = await open('#/czr-full-credit-assessment/model');
    check('Model: no fixture summary under any chart', $$('.wbc-sum').length === 0 && !/populated row/.test(text('#canvas')));
    check('Model: limitations read by name, the code is a secondary chip', $$('.mv-lim strong').every((s) => !/[A-Z]{3,}_[A-Z_]+/.test(s.textContent)) && $$('.mv-lim .mv-lc').some((c) => /PROJECTION_OPENING_AT_LTM/.test(c.textContent)) && !/sid_bonds/.test(text('#p-limitations')), text('#p-limitations').slice(0, 120));
    w = await open('#/czr-full-credit-assessment/module/CP-4');
    const markEl = $$('.wbc g.mk')[0];
    markEl.dispatchEvent(new w.MouseEvent('click', { bubbles: true }));
    await sleep(80);
    check('chart mark passport: figure in words, raw id small at the foot', !/@/.test(text('.pp-top') + text('.pp-title')) && /@/.test(text('.pp-id')), text('.pp-top') + ' / ' + text('.pp-id'));
    w = await open('#/czr-portfolio-decision/fit');
    check('limits: one state rule in every view (C-04 reads Tight in Portfolio Fit too)', /Tight/.test(text('#fl-TEST_CLO_I-C-04')), text('#fl-TEST_CLO_I-C-04').slice(0, 80));

    /* ---- C1 critique fixes ---- */
    // item 1: passports tell the truth
    w = await open('#/czr-full-credit-assessment/front');
    const kvRow = (label) => $$('.dt.kv[data-table="snapshot.company_profile"] tr').find((tr) => tr.querySelector('th') && tr.querySelector('th').textContent.trim() === label);
    const fitchChip = kvRow('Fitch') && kvRow('Fitch').querySelector('.gapchip');
    check('C1.1 Snapshot Fitch n/a chip present', fitchChip);
    if (fitchChip) {
      fitchChip.click();
      await until(() => $('.pp-title'));
      check('C1.1 passport title is the label on the page ("Fitch"), never "n/a: — · Corp rating fitch"', text('.pp-title') === 'Fitch', text('.pp-title'));
      check('C1.1 passport body drops the "—" row label', !/—|Corp rating/.test(text('.pp-f')), text('.pp-f'));
      const toks = $$('.pp-id .pp-tok');
      check('C1.1 foot id is whole tokens, never clipped mid-word (wrap or ellipsis on a whole token)', toks.length >= 2 && /corp_rating_fitch/.test(text('.pp-id')) && toks.every((t) => t.scrollWidth <= t.clientWidth + 1 || w.getComputedStyle(t).textOverflow === 'ellipsis'), toks.length + ' tokens: ' + text('.pp-id'));
    }
    // Equity's SSIM multiple: an n/a no gap in the Capital structure module states (counted as unresolved)
    const msChip = $('.dt[data-table="snapshot.capital_structure_totals"] tr[data-r="4"] .gapchip');
    check('C1.1 an n/a with no matching gap present (Capital structure totals, Equity, SSIM multiple)', msChip);
    if (msChip) {
      msChip.click();
      await until(() => $('.pp-title'));
      check('C1.1 no matching gap: "Reason not recorded by the module", no unrelated gaps listed', /Reason not recorded by the module/.test(text('.pp-f')) && !$('.pp-gaps') && !/No specific gap/.test(text('.pp-f')), text('.pp-f') + ' | gaps listed: ' + $$('.pp-gaps li').length);
      key(w, w.document.activeElement, 'Escape');
    }
    const stripMark = $$('#p-fp-strip .wbc g.mk-gap')[0];
    check('C1.1 Net leverage FY2023 n/a mark present', stripMark);
    if (stripMark) {
      stripMark.dispatchEvent(new w.MouseEvent('click', { bubbles: true }));
      await until(() => $('.pp-title'));
      check('C1.1 a chart mark drawn from a Model line shows its Model cell reason code and full reason', /COMPONENT_MISSING/.test(text('.pp-f')) && /Net leverage/.test(text('.pp-title')) && !/No specific gap/.test(text('.pp-f')) && !$('.pp-gaps'), text('.pp-title') + ' | ' + text('.pp-f').slice(0, 160));
    }
    check('C1.1 the module gap list is de-duplicated', (() => { const t = w.WB.gapItems('MODEL').map((g) => g.text.trim().toLowerCase()); return t.length > 0 && new Set(t).size === t.length; })(), w.WB.gapItems('MODEL').length + ' items');
    check('C1.1 unresolved n/a cells are counted: window.__wbUnresolvedGaps and html[data-unresolved] agree', Array.isArray(w.__wbUnresolvedGaps) && w.document.documentElement.dataset.unresolved === String(w.__wbUnresolvedGaps.length) && w.__wbUnresolvedGaps.length >= 1, String(w.document.documentElement.dataset.unresolved));
    w = await open('#/czr-full-credit-assessment/module/CP-1B');
    const citeChip = $$('button.cm')[0];
    if (citeChip) {
      citeChip.click();
      await until(() => $('.pp-title'));
      check('C1.1 a cited passport shows words for the origin, the raw locator only in the foot', !/\b(data|doc|caos|synthetic):/.test(text('.pp-f')) && /\b(data|doc|caos|synthetic|CP-\w+):/.test(text('.pp-id')), text('.pp-f').slice(0, 160) + ' | foot: ' + text('.pp-id'));
    } else check('C1.1 cite chip present on CP-1B', false);

    // item 2: main risk on every Front Page, notices as tags, bar height within W6's numbers
    const W6_BAR = { 'czr-full-credit-assessment': 255, 'czr-full-credit-assessment-quick': 298, 'czr-earnings-update': 301, 'czr-relative-value': 268, 'czr-relative-value-blocked': 297, 'czr-covenant-refinancing': 307, 'czr-portfolio-decision': 340, 'larchmere-distressed-restructuring': 301 };
    for (const runId of Object.keys(W6_BAR)) {
      w = await open('#/' + runId + '/front', [1440, 900]);
      const shown = $$('.verdict-lines > .v-line .v-ll').map((l) => l.textContent.trim());
      const folded = $$('.verdict-lines details .v-ll').map((l) => l.textContent.trim());
      check('C1.2 ' + runId + ': MAIN RISK is a call line that never folds', shown.includes('MAIN RISK') && !folded.includes('MAIN RISK'), 'shown=' + shown.join(',') + ' folded=' + folded.join(','));
      check('C1.2 ' + runId + ': no Blocked or Screening-basis call line', ![...shown, ...folded].some((l) => /^(BLOCKED|SCREENING BASIS)$/.test(l)), shown.concat(folded).join(','));
      const bh = $('.verdict').getBoundingClientRect().height + ($('.verdict-lines') ? $('.verdict-lines').getBoundingClientRect().height : 0);
      check('C1.2 ' + runId + ': bar height within W6 (' + W6_BAR[runId] + 'px)', bh <= W6_BAR[runId] + 2, Math.round(bh));
    }
    w = await open('#/czr-relative-value-blocked/front');
    const blockedTag = $('.v-meta .v-note');
    check('C1.2 Blocked is a tag in the byline row: word, icon and module code', blockedTag && /Blocked/.test(blockedTag.textContent) && /CP-3D/.test(blockedTag.textContent) && blockedTag.querySelector('svg'), blockedTag && blockedTag.textContent);
    w = await open('#/czr-full-credit-assessment-quick/front');
    const scrTag = $('.v-meta .v-note');
    check('C1.2 Screening basis is a tag in the byline row: word, icon and module code', scrTag && /Screening basis/i.test(scrTag.textContent) && /CP-\w+/.test(scrTag.textContent) && scrTag.querySelector('svg'), scrTag && scrTag.textContent);

    // item 3: laptop width
    for (const [runId, name, extra] of [['czr-full-credit-assessment', /Caesars Entertainment/, null], ['larchmere-distressed-restructuring', /Larchmere Leisure Group/, /Fictional/], ['czr-relative-value-blocked', /Caesars Entertainment/, null]]) {
      w = await open('#/' + runId + '/front', [1280, 800]);
      const vt = text('.v-head');
      const ii = $('.v-head .issuer-id');
      check('C1.3 ' + runId + ' @1280: the verdict bar title row names the issuer and ticker', ii && name.test(text('.ii-n', w)) && /^(CZR|LLG)$/.test(text('.ii-t', w)), ii && ii.textContent);
      if (extra) check('C1.3 ' + runId + ' @1280: the Fictional tag sits in the title row', extra.test(text('.v-head .ii-f', w)), vt.slice(0, 120));
    }
    for (const v of ['module/CP-1B', 'model', 'evidence', 'limitations', 'system']) {
      w = await open('#/czr-full-credit-assessment/' + v, [1280, 800]);
      check('C1.3 @1280 ' + v + ': the canvas header names the issuer', /Caesars Entertainment/.test(text('.m-bar')), text('.m-bar').slice(0, 100));
    }
    w = await open('#/czr-portfolio-decision/fit', [1280, 800]);
    check('C1.3 @1280 fit: the canvas header names the issuer', /Caesars Entertainment/.test(text('.m-bar')), text('.m-bar').slice(0, 100));
    w = await open('#/czr-full-credit-assessment/front', [1280, 800]);
    const iw = () => $('#inspector').getBoundingClientRect().width;
    check('C1.3 @1280 nothing selected: the inspector is a slim strip', iw() > 0 && iw() < 80, iw());
    const strip = $('.insp-open');
    check('C1.3 @1280 the strip is a labelled, keyboard-reachable control', strip && strip.tagName === 'BUTTON' && strip.getAttribute('aria-label') && strip.tabIndex >= 0 && strip.getBoundingClientRect().width > 0, strip && strip.getAttribute('aria-label'));
    const fig1 = $$('#canvas .fig-cited')[0] || $$('#canvas .fig')[0];
    fig1.focus();
    fig1.click();
    await sleep(80);
    check('C1.3 @1280 selecting a figure opens the inspector at full width', iw() === 300, iw());
    key(w, w.document.activeElement, 'Escape');
    await sleep(80);
    check('C1.3 @1280 closing returns to the strip and focus returns to the figure', iw() < 80 && w.document.activeElement === fig1, iw() + ' / ' + (w.document.activeElement && w.document.activeElement.className));
    if ($('.insp-open')) {
      $('.insp-open').click();
      await sleep(80);
      check('C1.3 @1280 the strip opens the inspector empty', iw() === 300 && /Select a figure/.test(text('.insp-body')), iw());
      key(w, w.document.activeElement, 'Escape');
      await sleep(80);
      check('C1.3 @1280 closing an empty inspector returns to the strip', iw() < 80, iw());
    }
    w = await open('#/czr-full-credit-assessment/front', [1440, 900]);
    const fig2 = $$('#canvas .fig')[0];
    fig2.focus();
    fig2.click();
    await sleep(80);
    key(w, w.document.activeElement, 'Escape');
    await sleep(60);
    check('C1.3 @1440 unchanged: the inspector stays full width and keeps its passport after Esc', $('#inspector').getBoundingClientRect().width === 300 && !!$('.pp-title') && w.document.activeElement === fig2, $('#inspector').getBoundingClientRect().width);

    // item 4: spend signal only where it means something
    w = await open('#/czr-full-credit-assessment/front');
    check('C1.4 Illustrative is stated once at page level: the verdict bar has it, no panel carries the tag', $('.v-tag') && $$('.panel .tag-illustrative').length === 0, $$('.panel .tag-illustrative').length + ' panel tags');
    check('C1.4 a synthetic panel on an illustrative page keeps its own tag', $$('.panel .tag-synthetic').length >= 1, $$('.panel .tag-synthetic').length);
    for (const runId of ['czr-full-credit-assessment', 'czr-relative-value-blocked']) {
      w = await open('#/' + runId + '/front');
      const rowsN = $$('.nav-row').map((a) => ({ st: (a.getAttribute('title') || '').split(': ').pop(), icon: !!a.querySelector('.nr-i svg'), label: a.getAttribute('aria-label') || '' }));
      const tally = {};
      rowsN.forEach((r) => (tally[r.st] = (tally[r.st] || 0) + 1));
      const mode = Object.keys(tally).sort((a, b) => tally[b] - tally[a])[0];
      check('C1.4 ' + runId + ' navigator: the icon shows only where a row departs from the run norm (' + mode + ')', rowsN.length > 5 && rowsN.every((r) => r.icon === (r.st !== mode)), JSON.stringify(tally));
      check('C1.4 ' + runId + ' navigator: the status word stays in every row\'s accessible name and tooltip', rowsN.every((r) => r.st && r.label.indexOf(r.st) >= 0), rowsN.slice(0, 2).map((r) => r.label).join(' | '));
    }
    for (const hash of ['#/czr-full-credit-assessment/front', '#/czr-full-credit-assessment/model', '#/czr-covenant-refinancing/front']) {
      w = await open(hash, [1440, 900]);
      const small = {};
      const wk = w.document.createTreeWalker(w.document.body, 4);
      let tn;
      while ((tn = wk.nextNode())) {
        const pe = tn.parentElement;
        if (!tn.nodeValue.trim() || !pe || pe.closest('script,style,.sr-only,svg')) continue;
        const r = pe.getBoundingClientRect();
        if (!r.width || !r.height) continue;
        const fs = parseFloat(w.getComputedStyle(pe).fontSize);
        if (fs < 10.99) small[(pe.className || pe.tagName) + ' ' + fs] = 1;
      }
      check('C1.4 ' + hash + ': no text below 11px (type floor)', Object.keys(small).length === 0, Object.keys(small).slice(0, 6).join(' | '));
    }
    w = await open('#/czr-full-credit-assessment/front');
    const tag1 = $$('.tag-synthetic')[0];
    check('C1.4 --fs-micro and .tag are 11px, the tag has a vertical inset', w.getComputedStyle(w.document.documentElement).getPropertyValue('--fs-micro').trim() === '11px' && (!tag1 || (w.getComputedStyle(tag1).fontSize === '11px' && parseFloat(w.getComputedStyle(tag1).paddingTop) >= 1)), tag1 ? w.getComputedStyle(tag1).fontSize + ' pad ' + w.getComputedStyle(tag1).paddingTop : 'no tag');
    const vl = $('.verdict-lines .v-line');
    check('C1.4 call-line prose is capped near 90ch (no wider than 760px at 12px)', vl && vl.getBoundingClientRect().width <= 760, vl && Math.round(vl.getBoundingClientRect().width));

    // item 5: numbers by unit
    w = await open('#/czr-relative-value/front');
    const callTxt = text('.verdict-lines');
    check('C1.5 call line: yields to 2 dp (8.06%, 9.32%), never 8.06352% or 9.318398%', !/\d\.\d{3,}%/.test(callTxt) && /8\.06%/.test(callTxt) && /9\.32%/.test(callTxt), callTxt.slice(callTxt.indexOf('PREFERRED'), callTxt.indexOf('PREFERRED') + 160));
    const longNums = $$('#canvas td.c-num .fv').map((f) => f.textContent.trim()).filter((t) => /^\d+\.\d{3,}%?$/.test(t));
    check('C1.5 table cells: yields and prices to 2 dp (no 3 to 6 dp yields or prices)', longNums.length === 0, longNums.slice(0, 6).join(' '));
    w = await open('#/larchmere-distressed-restructuring/front');
    const cap = text('#canvas');
    check('C1.5 EV in whole millions with grouping (1,407, not 1,406.5), in tables and charts', /1,407/.test(cap) && !/1,406\.5/.test(cap), (/.{30}1,40[67][.\d]*.{10}/.exec(cap) || [''])[0]);
    const ev = text('.dt[data-table="cp4c.ev_scenarios"]');
    check('C1.5 EV scenarios in whole millions', ev === '' || !/\d,\d{3}\.\d/.test(ev), ev.slice(0, 120));
    w = await open('#/czr-full-credit-assessment/model');
    const bigCell = (() => { for (const l of w.WB.run.model.lines) for (const c of l.cells) if (c.value != null && Math.abs(+c.value) >= 10000) return { lineId: l.line_id, columnId: c.column_id }; return null; })();
    check('C1.5 the passport "Served as" is grouped', bigCell && (() => { const p = w.WB.buildPassport({ t: 'mcell', lineId: bigCell.lineId, columnId: bigCell.columnId }); const sv = p.fields.find((f) => f[0] === 'Served as'); return sv && /^\(?\d{1,3}(,\d{3})+/.test(sv[1]); })(), bigCell && JSON.stringify(w.WB.buildPassport({ t: 'mcell', lineId: bigCell.lineId, columnId: bigCell.columnId }).fields[0]));

    // item 6: brand mark and the silent catch
    w = await open('#/czr-full-credit-assessment/front');
    const logo = $('.rail-logo');
    const logoUrl = (/url\("?([^")]+)"?\)/.exec(w.getComputedStyle(w.document.documentElement).getPropertyValue('--logo-url')) || [])[1];
    const dim = await new Promise((res) => { const im = new w.Image(); im.onload = () => res([im.naturalWidth, im.naturalHeight]); im.onerror = () => res(null); im.src = logoUrl; });
    check('C1.6 the rail logo is the wave icon only (no wordmark): the asset is near-square', dim && dim[0] / dim[1] < 1.6, dim && dim.join('x'));
    check('C1.6 the rail logo keeps role=img and its accessible name, and shows the whole icon', logo && logo.getAttribute('role') === 'img' && /State Street/.test(logo.getAttribute('aria-label')) && dim && Math.abs(logo.getBoundingClientRect().width / logo.getBoundingClientRect().height - dim[0] / dim[1]) < 0.15, logo && logo.getBoundingClientRect().width + 'x' + logo.getBoundingClientRect().height);
    w = await open('#/czr-full-credit-assessment/system');
    check('C1.6 the Design system specimen search does not swallow errors silently: it logs a count or none were thrown', w.document.documentElement.dataset.errors === '0' && typeof w.__wbSpecimenSkips === 'number', String(w.__wbSpecimenSkips));

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
