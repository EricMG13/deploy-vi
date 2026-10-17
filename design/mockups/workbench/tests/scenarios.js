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
  async function open(hash, size, search) {
    if (size) {
      frame.style.width = size[0] + 'px';
      frame.style.height = size[1] + 'px';
    }
    frame.src = 'about:blank';
    await sleep(20);
    frame.src = BASE + (search || '') + hash;
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
    await until(() => $('.rs-row'));
    check('run switcher lists eight runs', $$('.rs-row').length === 8, $$('.rs-row').length);
    check('run switcher groups by Pathway', $$('.rs-g').length === 6, $$('.rs-g').length);
    key(w, w.document.body, 'Escape');
    await sleep(60);
    // the real-run switch lives in the verdict bar (C2.3)
    $('.v-state').click();
    await sleep(300);
    const after = $$('.tile-sq.np').length;
    check('honest state: Not produced tiles appear', before === 0 && after >= 4, before + ' -> ' + after);
    check('honest state: reason and producing module named', $$('.tile .tile-why').length >= 4 && $$('.tile .tile-mod').length >= 4, text('.tile-why'));
    check('honest state: a Not produced tile opens its reason as a passport', (() => { const b = $$('.tile .tile-btn').find((x) => /not produced/i.test(x.getAttribute('aria-label') || '')); if (!b) return false; b.click(); return /not produced/i.test(text('.pp-title')) && /Reason/.test(text('.pp-f')); })(), text('.pp-title'));
    $('.nav-issuer').click();
    await until(() => $('.rs-row'));
    key(w, w.document.body, 'Escape');
    await sleep(50);
    check('Escape closes the run switcher', !$('.rs'));
    $('.v-state').click();
    await sleep(150);

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
    // C2: with the lines shorter (a bold lead, one Sources button) the Earnings Update bar shows all four lines; nothing folds
    check('call: the four Earnings Update lines show, in the content doc order (C2: Watch no longer folds)', visibleLines.join(',') === 'THE QUARTER,MAIN RISK,NO RECOMMENDATION,WATCH', visibleLines.join(','));
    check('call: a bar with every line showing has no disclosure', !$('.verdict-lines details.v-more'), text('.v-more-s'));
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
    // C2: ceilings revisited. A breach is never folded and a capped Strategy tile carries its badge, so the bars grew (the budget gives way): the numbers are C2's measured heights plus 10px
    const W6_BAR = { 'czr-full-credit-assessment': 270, 'czr-full-credit-assessment-quick': 290, 'czr-earnings-update': 310, 'czr-relative-value': 275, 'czr-relative-value-blocked': 275, 'czr-covenant-refinancing': 330, 'czr-portfolio-decision': 375, 'larchmere-distressed-restructuring': 440 };
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
    // below 1360px the inspector's column is always the 36px strip; the open pane is an overlay, so its width is the pane's
    const iw = () => { const pn = $('.insp-pane'); return pn && pn.getBoundingClientRect().width > 0 ? pn.getBoundingClientRect().width : $('#inspector').getBoundingClientRect().width; };
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

    {
    /* =====================================================================================================
       C2: second-critique fixes. Each check names the reported cause; the block ran red on the build at 2154cce.
       ===================================================================================================== */
    const RUNS8 = ['czr-full-credit-assessment', 'czr-full-credit-assessment-quick', 'czr-earnings-update', 'czr-relative-value', 'czr-relative-value-blocked', 'czr-covenant-refinancing', 'czr-portfolio-decision', 'larchmere-distressed-restructuring'];
    const llabel = (p) => (p.querySelector('.v-ll') ? p.querySelector('.v-ll').textContent.trim() : '');
    const rectOf = (n) => n.getBoundingClientRect();
    const tx = (sel, root) => ((root.querySelector(sel) || {}).textContent || '').trim();
    const hit = (a, b) => a.left < b.right && a.right > b.left && a.top < b.bottom && a.bottom > b.top;

    /* ---- C2.1 breaches are never hidden ---- */
    for (const runId of RUNS8) {
      w = await open('#/' + runId + '/front', [1440, 900]);
      const foldedNeg = $$('.verdict-lines details .v-line').filter((p) => p.querySelector('.v-ll.tone-neg') || p.querySelector('.v-verdict.tone-neg')).map(llabel);
      check('C2.1 ' + runId + ': no negative call line folds into "more"', foldedNeg.length === 0, foldedNeg.join(','));
      const fitBad = $$('.verdict-lines .v-line').filter((p) => p.querySelector('.v-verdict.tone-neg') && !p.querySelector('.v-ll.tone-neg')).map(llabel);
      check('C2.1 ' + runId + ': a Fit line that carries Breaches reads as a negative line', fitBad.length === 0, fitBad.join(','));
    }
    for (const sz of [[1440, 900], [1280, 800]]) {
      w = await open('#/larchmere-distressed-restructuring/front', sz);
      const shown = $$('.verdict-lines > .v-line').map(llabel);
      check('C2.1 Larchmere @' + sz[0] + ': Fit (Breaches), the gate (Met), fulcrum and main risk all show', ['PORTFOLIO FIT', 'GATE', 'FULCRUM', 'MAIN RISK'].every((l) => shown.includes(l)), shown.join(','));
    }
    for (const sz of [[1440, 900], [1280, 800]]) {
      w = await open('#/czr-portfolio-decision/front', sz);
      const segs = $$('.verdict-lines .v-fit');
      check('C2.1 Portfolio Decision @' + sz[0] + ': one unbreakable segment per portfolio (name, tag, counts, Details)', segs.length === 2 && segs.every((s) => s.querySelector('.v-verdict') && s.querySelector('.v-lnk')) && /Test CLO I/.test(segs[0].textContent) && /Test Indexed HY I/.test(segs[1].textContent), segs.map((s) => s.textContent).join(' | '));
      check('C2.1 Portfolio Decision @' + sz[0] + ': the Breaches count sits in the Indexed HY segment, not under the CLO name', segs.length === 2 && /1 Breaches/.test(segs[1].textContent) && !/Breaches/.test(segs[0].textContent), segs.map((s) => s.textContent).join(' | '));
      check('C2.1 Portfolio Decision @' + sz[0] + ': no segment wraps onto a second line', segs.length === 2 && segs.every((s) => s.getClientRects().length === 1 && rectOf(s).height < 24), segs.map((s) => Math.round(rectOf(s).height)).join(','));
    }
    const capExpect = (strat) => {
      const t = frame.contentWindow.WB.table('cp6.portfolio_recommendation');
      if (!t) return null;
      const ix = (n) => t.columns.indexOf(n);
      const rows = t.rows.filter((r) => r[ix('strategy')] === strat);
      if (!rows.length) return null;
      const br = rows.filter((r) => r[ix('fit_verdict')] === 'Breaches');
      const cp = rows.filter((r) => r[ix('final')] !== r[ix('uncapped')]);
      const use = br.length ? br : cp.filter((r) => r[ix('fit_verdict')] !== 'Breaches');
      return { breach: br.length, capped: cp.length, cap: Array.from(new Set(use.map((r) => r[ix('cap')]))) };
    };
    for (const runId of ['larchmere-distressed-restructuring', 'czr-portfolio-decision', 'czr-full-credit-assessment']) {
      w = await open('#/' + runId + '/front', [1440, 900]);
      for (const strat of ['CLO', 'Indexed Loans', 'Indexed HY']) {
        const tile = $$('.v-tiles .tile').find((t) => tx('.tile-l', t) === strat || (t.querySelector('.tile-l') && t.querySelector('.tile-l').textContent.trim() === strat));
        const ex = capExpect(strat);
        const badge = tile && tile.querySelector('.tile-cap');
        if (ex && (ex.breach || ex.capped)) {
          check('C2.1 ' + runId + ': the ' + strat + ' tile says its Recommendation is capped by Fit (word and icon, the run’s own cap)', badge && /Capped by Fit/.test(badge.textContent) && badge.querySelector('svg') && (ex.cap.length !== 1 || badge.textContent.includes(ex.cap[0])) && (!ex.breach || badge.classList.contains('tone-neg')), badge ? badge.textContent : 'no badge ' + JSON.stringify(ex));
        } else check('C2.1 ' + runId + ': the ' + strat + ' tile with no Fit cap carries no badge', !badge, badge && badge.textContent);
      }
    }

    /* ---- C2.2 provenance on every value ---- */
    w = await open('#/czr-full-credit-assessment/front');
    const kvRow = (re) => $$('.kv tr').find((tr) => re.test(tr.textContent));
    const moody = kvRow(/Moody/);
    const moodyFig = moody && moody.querySelector('button.fig[data-ref]');
    check('C2.2 the Moody’s rating is a focusable figure with a passport (the row cites a synthetic source)', moodyFig && moodyFig.classList.contains('fig-synthetic') && /B1/.test(moodyFig.textContent), moody && moody.innerHTML.slice(0, 160));
    if (moodyFig) {
      moodyFig.click();
      await sleep(60);
      check('C2.2 the rating passport is SYNTHETIC and names TEST DATA', /SYNTHETIC/.test(text('.pp-kind')) && /TEST DATA/.test(text('.pp-f') + text('.pp-ex')), text('.pp-kind') + ' | ' + text('.pp-f').slice(0, 80));
    }
    const spRow = kvRow(/S&P/);
    check('C2.2 the S&P rating and its outlook are figures too', spRow && spRow.querySelectorAll('button.fig[data-ref]').length >= 2, spRow && spRow.querySelectorAll('button.fig[data-ref]').length);
    const sectorRow = kvRow(/Sector/);
    check('C2.2 sector and country (short text in a citing row) are figures', sectorRow && sectorRow.querySelector('button.fig[data-ref]') && kvRow(/Country/).querySelector('button.fig[data-ref]'), sectorRow && sectorRow.innerHTML.slice(0, 120));
    // every text value in a row that cites a source resolves to cited or synthetic; plain only when the row cites nothing
    // (the row-label column of a multi-row table and unit descriptors stay plain)
    const plainText = [];
    for (const runId of RUNS8) {
      const wr = await open('#/' + runId + '/front');
      for (const [tid, t] of wr.WB.run._tables) {
        if (tid.indexOf('@') >= 0 || t.columns.indexOf('cite') < 0) continue;
        const kinds = wr.WB.columnKinds(t);
        const lead = kinds.findIndex((k) => k.kind !== 'hidden' && !/_id$/.test(k.name));
        kinds.forEach((k, c) => {
          if (k.kind !== 'text' || k.modelWritten || /^(unit_label|unit|currency)$/.test(k.name) || (t.rows.length > 1 && c === lead)) return;
          t.rows.forEach((row, r) => {
            const info = wr.WB.rowInfo(t, r);
            if (info && info.cites.length && !wr.WB.isEmpty(row[c]) && wr.WB.cellOrigin(t, r, c).kind === 'plain') plainText.push(runId + ':' + tid + '.' + k.name + '#' + r);
          });
        });
      }
      if (plainText.length > 3) break;
    }
    check('C2.2 no text value in a citing row resolves to plain', plainText.length === 0, plainText.length + ' e.g. ' + plainText.slice(0, 3).join(' | '));
    w = await open('#/czr-relative-value/front');
    {
      const t = $('.dt[data-table="snapshot.instrument_levels"]');
      const heads = t ? Array.from(t.querySelectorAll('thead th')).map((h) => h.textContent.trim()) : [];
      const ix = heads.findIndex((h) => /coupon/i.test(h));
      const cells = t && ix >= 0 ? Array.from(t.querySelectorAll('tbody tr[data-r]')).map((tr) => tr.children[ix]).filter((td) => td && td.textContent.trim()) : [];
      const dix = heads.findIndex((h) => /level date/i.test(h));
      const dcells = t && dix >= 0 ? Array.from(t.querySelectorAll('tbody tr[data-r]')).map((tr) => tr.children[dix]).filter((td) => td && td.textContent.trim()) : [];
      check('C2.2 Relative Value: every level date is a figure with a passport (a date is a stated value)', dcells.length >= 4 && dcells.every((td) => td.querySelector('button.fig[data-ref], .gapchip')), dcells.length + ' cells, ' + dcells.filter((td) => !td.querySelector('button.fig[data-ref], .gapchip')).length + ' plain');
      check('C2.2 Relative Value: every coupon / spread value is a figure with a passport', cells.length >= 4 && cells.every((td) => td.querySelector('button.fig[data-ref], .gapchip')), cells.length + ' cells, ' + cells.filter((td) => !td.querySelector('button.fig[data-ref], .gapchip')).length + ' plain');
    }
    // a figure with no source stated: a visible mark and a passport that says so
    w = await open('#/czr-full-credit-assessment/front');
    const nones = $$('#canvas .fig-none');
    check('C2.2 a no-source figure is on the page (EV 17,600, Equity 1,758)', nones.length >= 2, nones.length);
    check('C2.2 every no-source figure carries a visible mark of its own shape', nones.length >= 2 && nones.every((n) => { const m = n.querySelector('svg.mk-none'); return m && rectOf(m).width > 4; }), nones.map((n) => !!n.querySelector('svg.mk-none')).join(','));
    if (nones[0]) {
      nones[0].click();
      await sleep(60);
      check('C2.2 a no-source passport says "No source stated by the module" with the row’s context', /NO SOURCE STATED/i.test(text('.pp-kind')) && /No source stated by the module/.test(text('.pp-f')) && /(Equity|Enterprise|EV)/i.test(text('.pp-title') + text('.pp-f')), text('.pp-kind') + ' | ' + text('.pp-title') + ' | ' + text('.pp-f').slice(0, 160));
    }
    // every gap chip's accessible name carries its reason
    for (const runId of ['czr-full-credit-assessment', 'czr-covenant-refinancing', 'larchmere-distressed-restructuring', 'czr-relative-value']) {
      w = await open('#/' + runId + '/front');
      const bare = $$('.gapchip').filter((g) => !/[:,] ?.{6,}/.test((g.getAttribute('aria-label') || '').replace(/^Not available/, '')) || /^Not available(, [^:]*)?$/.test(g.getAttribute('aria-label') || ''));
      check('C2.2 ' + runId + ': every gap chip’s accessible name includes its reason', $$('.gapchip').length > 0 && bare.length === 0, bare.length + ' bare of ' + $$('.gapchip').length + ' e.g. ' + (bare[0] && bare[0].getAttribute('aria-label')));
    }
    // the key sheet and the Design system carry the new kind
    w.document.querySelector('.rail-btn[aria-label^="How to read"]').click();
    await sleep(80);
    check('C2.2 the ? key sheet lists "No source stated" with its own mark', /No source stated/.test(text('.hk')) && $('.hk .mk-none'), text('.hk').slice(0, 80));
    w = await open('#/czr-full-credit-assessment/system');
    check('C2.2 the Design system’s provenance specimens include the no-source kind (mark and passport)', $('#ds-marks .mk-none, [id$="marks"] .mk-none') && /No source stated by the module/.test(text('#ds-passports, [id$="passports"]') || text('#canvas')), !!$('.mk-none'));

    /* ---- C2.3 a complete honest state ---- */
    const NP_OK = new Set(['Covenant tests', 'Distress gate']);
    for (const runId of RUNS8) {
      w = await open('#/' + runId + '/front', [1440, 900], '?state=real');
      const tiles = $$('.v-tiles .tile');
      const leftover = tiles.filter((t) => !t.querySelector('.tile-sq.np') && !NP_OK.has(tx('.tile-l', t))).map((t) => tx('.tile-l', t) + '=' + tx('.tile-word', t));
      check('C2.3 ' + runId + ': in the real-run state no judgement tile shows a fixture value (state read from the URL)', tiles.length > 0 && leftover.length === 0 && $$('.tile-sq.ill').length === 0, leftover.join(', '));
      check('C2.3 ' + runId + ': every Not produced tile gives a reason and its producing module', $$('.tile-sq.np').length > 0 && tiles.filter((t) => t.querySelector('.tile-sq.np')).every((t) => t.querySelector('.tile-why') && tx('.tile-why', t).length > 8 && t.querySelector('.tile-mod')), '');
      check('C2.3 ' + runId + ': the bar’s ILLUSTRATIVE tag becomes REAL-RUN STATE', /REAL-RUN STATE/.test(text('.v-meta .v-tag')) && !/ILLUSTRATIVE/.test(text('.v-meta')), text('.v-meta .v-tag'));
    }
    w = await open('#/czr-earnings-update/front', [1440, 900], '?state=real');
    check('C2.3 Earnings Update: Direction, Sector Outlook and Since last Report give the run’s own gap text', ['Credit Direction', 'Sector Outlook', 'Since last Report'].every((l) => { const t = $$('.v-tiles .tile').find((x) => tx('.tile-l', x) === l); return t && /never produced|no earlier|real run/i.test(t.querySelector('.tile-btn').getAttribute('aria-label')); }), $$('.v-tiles .tile .tile-btn').map((b) => b.getAttribute('aria-label').slice(0, 60)).join(' | '));
    w = await open('#/czr-full-credit-assessment/front', [1440, 900]);
    check('C2.3 the toggle sits in the verdict bar header beside the tag: a labelled switch with aria-pressed', $('.v-meta .v-state') && $('.v-meta .v-state').tagName === 'BUTTON' && $('.v-meta .v-state').getAttribute('aria-pressed') === 'false' && /real-run state/i.test($('.v-meta .v-state').textContent) && $('.v-meta .v-state').tabIndex >= 0 && $('.v-meta .v-state').parentNode === $('.v-meta .v-tag').parentNode, $('.v-meta .v-state') && $('.v-meta .v-state').outerHTML.slice(0, 120));
    check('C2.3 the normal bar keeps its ILLUSTRATIVE tag', /ILLUSTRATIVE/.test(text('.v-meta .v-tag')), text('.v-meta .v-tag'));
    if ($('.v-state')) {
      $('.v-state').click();
      await sleep(250);
      check('C2.3 pressing the switch turns the state on: aria-pressed, REAL-RUN STATE, Not produced tiles', $('.v-state') && $('.v-state').getAttribute('aria-pressed') === 'true' && /REAL-RUN STATE/.test(text('.v-meta .v-tag')) && $$('.tile-sq.np').length === 6, $$('.tile-sq.np').length);
      check('C2.3 the state is in the URL so it survives reload and can be shared', /[?&]state=real/.test(w.location.search), w.location.href.slice(-60));
      $('.v-state').click();
      await sleep(250);
      check('C2.3 turning it off clears the URL flag', !/state=real/.test(w.location.search) && $$('.tile-sq.np').length === 0, w.location.search);
    }
    w = await open('#/czr-full-credit-assessment/front', null, '?state=real');
    check('C2.3 a reload with the flag restores the real-run state', $('.v-state') && $('.v-state').getAttribute('aria-pressed') === 'true' && $$('.tile-sq.np').length === 6, $$('.tile-sq.np').length);
    $('.nav-issuer').click();
    await until(() => $('.rs-row'));
    check('C2.3 the run switcher no longer carries the toggle (it moved to the bar)', !$('.rs-switch'), !!$('.rs-switch'));
    key(w, w.document.body, 'Escape');
    // the panels below the bar: illustrative verdicts are dimmed and labelled while the real-run state is on
    w = await open('#/larchmere-distressed-restructuring/front', [1440, 900]);
    const gateBadge = () => $('.dt[data-table="cp4c.distress_gate"] .badge');
    const normalColour = gateBadge() ? w.getComputedStyle(gateBadge()).color : null;
    check('C2.3 Larchmere (normal): no panel is labelled as the fixture’s own view', $$('.panel .tag-fixture').length === 0, $$('.panel .tag-fixture').length);
    w = await open('#/larchmere-distressed-restructuring/front', [1440, 900], '?state=real');
    const gatePanel = $('.dt[data-table="cp4c.distress_gate"]') && $('.dt[data-table="cp4c.distress_gate"]').closest('.panel');
    check('C2.3 Larchmere (real-run): the gate panel is labelled "Fixture’s own view"', gatePanel && /Fixture.s own view/.test(tx('.tag-fixture', gatePanel)), gatePanel && gatePanel.querySelector('.p-l').textContent.slice(0, 100));
    const dimmed = gateBadge() ? w.getComputedStyle(gateBadge()).color : null;
    const probeSpan = w.document.createElement('span');
    probeSpan.style.color = 'var(--ink-2)';
    w.document.body.appendChild(probeSpan);
    const ink2 = w.getComputedStyle(probeSpan).color;
    check('C2.3 Larchmere (real-run): the Met / Not met words under the Not met bar are no longer a signal colour', normalColour && dimmed && normalColour !== dimmed && dimmed === ink2, normalColour + ' -> ' + dimmed + ' (ink-2 ' + ink2 + ')');
    check('C2.3 Larchmere (real-run): the bar reads Not met, REAL-RUN STATE', /Not met/.test(text('.v-tiles')) && /REAL-RUN STATE/.test(text('.v-tag')), text('.v-tiles').slice(0, 60));
    w = await open('#/czr-full-credit-assessment/front', [1440, 900], '?state=real');
    check('C2.3 Snapshot (real-run): panels that hold illustrative verdicts are labelled "Fixture’s own view"', $$('.panel .tag-fixture').length >= 1, $$('.panel .tag-fixture').length);

    /* ---- C2.4 call lines read as a call ---- */
    for (const runId of RUNS8) {
      w = await open('#/' + runId + '/front', [1440, 900]);
      const lines = $$('.verdict-lines .v-line');
      const glyphs = $$('.verdict-lines .v-line .mk, .verdict-lines .v-line .cm, .verdict-lines .v-line .gapchip, .verdict-lines .v-line .calc-inline, .verdict-lines .v-line .fig, .verdict-lines .v-line .fpa-ref');
      check('C2.4 ' + runId + ': no per-clause glyph, code or figure button inside the bar’s prose', glyphs.length === 0, glyphs.length + ' e.g. ' + (glyphs[0] && glyphs[0].className));
      const bad = [];
      lines.forEach((p) => {
        const l = llabel(p);
        if (l === 'PORTFOLIO FIT') return;
        const lead = p.querySelector('.v-lead');
        const body = p.textContent.replace(l, '').replace(/\s+/g, ' ').trim();
        const lt = lead ? lead.textContent.trim() : '';
        const rest = body.slice(body.indexOf(lt) + lt.length);
        if (!lead || !lt || !body.startsWith(lt) || !(rest === '' || /^[,;:.]/.test(rest.trimStart()) || /^[,;:.]/.test(rest))) bad.push(l + ' lead=' + JSON.stringify(lt) + ' next=' + JSON.stringify(rest.slice(0, 6)));
        else if (lt.length > 120) bad.push(l + ' lead too long ' + lt.length);
      });
      check('C2.4 ' + runId + ': each line is label, a bold lead from its own first clause, then the rest', lines.length > 0 && bad.length === 0, bad.join(' | '));
      const srcBad = [];
      lines.forEach((p) => {
        const b = p.querySelectorAll('button.v-src');
        const others = Array.from(p.querySelectorAll('button')).filter((x) => !x.classList.contains('v-src') && !x.classList.contains('v-verdict'));
        const last = p.lastElementChild;
        if (b.length > 1 || others.length || (b.length === 1 && last !== b[0])) srcBad.push(llabel(p) + ' src=' + b.length + ' other=' + others.length);
        if (b.length === 1 && !(/^Sources \d+( · \d+ gaps?)?$|^\d+ gaps?$/.test(b[0].textContent.trim()) && /^Sources, \d+|^\d+ gaps?/.test(b[0].getAttribute('aria-label')))) srcBad.push(llabel(p) + ' label=' + b[0].textContent + ' aria=' + b[0].getAttribute('aria-label'));
      });
      check('C2.4 ' + runId + ': each line ends in one "Sources n" affordance (screen reader: one sentence, then "Sources, n")', lines.length > 0 && srcBad.length === 0, srcBad.join(' | '));
      const probe = w.document.createElement('span');
      probe.style.cssText = 'display:block;width:80ch;height:0;visibility:hidden';
      lines[0].appendChild(probe);
      const ch80 = rectOf(probe).width;
      probe.remove();
      const wide = lines.filter((p) => rectOf(p).width > ch80 + 2).map(llabel);
      check('C2.4 ' + runId + ': line measure is about 80ch', lines.length > 0 && wide.length === 0, wide.join(',') + ' (80ch = ' + Math.round(ch80) + 'px; widest ' + Math.round(Math.max.apply(null, lines.map((p) => rectOf(p).width))) + ')');
      check('C2.4 ' + runId + ': no sentence about the test run sits in a call line', !/test run|design fixture/i.test($('.verdict-lines').textContent), (/.{20}(test run|design fixture).{20}/i.exec($('.verdict-lines').textContent) || [''])[0]);
    }
    w = await open('#/czr-full-credit-assessment/front', [1440, 900]);
    {
      const mr = $$('.verdict-lines .v-line').find((p) => llabel(p) === 'MAIN RISK');
      const src = mr && mr.querySelector('.v-src');
      check('C2.4 Snapshot main risk: "Sources 2 · 1 gap" (C12, C13 and G8)', src && /^Sources 2 · 1 gap$/.test(src.textContent.trim()), src && src.textContent);
      check('C2.4 the main-risk lead is the text before its first comma, semicolon or colon (or the whole sentence)', mr && /Merger debt of unstated size on top of falling Las Vegas earnings/.test(tx('.v-lead', mr)), mr && tx('.v-lead', mr));
      if (src) {
        src.click();
        await sleep(80);
        const chips = $$('.pp-chips .pchip');
        check('C2.4 the Sources passport lists every citation and gap of the line, each a chip', chips.length === 3 && chips.filter((c) => /^C\d+/.test(c.textContent)).length === 2 && chips.some((c) => /G8/.test(c.textContent)), chips.map((c) => c.textContent.slice(0, 30)).join(' | '));
        if (chips[0]) {
          chips[0].click();
          await sleep(60);
          check('C2.4 a citation chip opens its own passport with Back', $('.pp-back') && /CITED|SYNTHETIC/.test(text('.pp-kind')) && $('.pp-ex'), text('.pp-kind') + ' ' + text('.pp-title'));
          $('.pp-back').click();
          await sleep(40);
          const gapChip = $$('.pp-chips .pchip').find((c) => /G8/.test(c.textContent));
          if (gapChip) {
            gapChip.click();
            await sleep(60);
            check('C2.4 a gap chip opens its own gap passport', /N\/A/i.test(text('.pp-kind')), text('.pp-kind'));
          } else check('C2.4 a gap chip opens its own gap passport', false, 'no G8 chip after Back');
        }
      }
      const fix = $('.v-by .v-fix');
      check('C2.4 the Design-fixture byline tag is a button', fix && fix.tagName === 'BUTTON' && fix.getAttribute('data-ref'), fix && fix.outerHTML.slice(0, 100));
      if (fix) {
        fix.click();
        await sleep(60);
        check('C2.4 its passport holds the moved fixture sentence, verbatim', /This test run uses three synthetic tranches in its place\./.test(text('.pp-f') + text('.pp-note') + text('.pp-title')), text('.pp-f').slice(0, 160));
      }
    }
    w = await open('#/larchmere-distressed-restructuring/front', [1440, 900]);
    {
      const mr = $$('.verdict-lines .v-line').find((p) => llabel(p) === 'MAIN RISK');
      check('C2.4 Larchmere main risk: lead "Cash earnings no longer cover fixed charges", Sources 3', mr && tx('.v-lead', mr) === 'Cash earnings no longer cover fixed charges' && /^Sources 3$/.test(tx('.v-src', mr)), mr && tx('.v-lead', mr) + ' | ' + tx('.v-src', mr));
    }
    w = await open('#/czr-covenant-refinancing/front', [1440, 900]);
    check('C2.4 Covenant & Refinancing: its call columns are plain figures with one Sources affordance per line (no marked mono figures)', $$('.verdict-lines .v-line').length >= 4 && $$('.verdict-lines .fig').length === 0 && $$('.verdict-lines .v-line .v-src').length >= 3, $$('.verdict-lines .fig').length + ' figs, ' + $$('.verdict-lines .v-src').length + ' src');

    /* ---- C2.5 the inspector at laptop width opens over the canvas, without reflow ---- */
    w = await open('#/czr-full-credit-assessment/front', [1280, 800]);
    {
      const grid0 = w.getComputedStyle($('#app')).gridTemplateColumns;
      const canvas0 = rectOf($('#canvas')).width;
      const bar0 = rectOf($('.verdict')).width;
      // the figure furthest to the right on the page, scrolled to the middle of the view: the overlay's default side would cover it
      const fig = $$('#canvas .fig').filter((f) => rectOf(f).width > 0).sort((a, b) => rectOf(b).right - rectOf(a).right)[0];
      fig.scrollIntoView({ block: 'center' });
      await sleep(60);
      check('C2.5 a figure near the right edge exists to select', fig && rectOf(fig).right > 1280 - 330, fig && Math.round(rectOf(fig).right));
      const before = rectOf(fig);
      fig.focus();
      fig.click();
      await sleep(150);
      const pane = $('.insp-pane');
      check('C2.5 @1280 selecting opens the inspector as an overlay: the #app grid is unchanged', w.getComputedStyle($('#app')).gridTemplateColumns === grid0, grid0 + ' -> ' + w.getComputedStyle($('#app')).gridTemplateColumns);
      check('C2.5 @1280 no layout in the canvas moves (canvas, verdict bar, the figure)', Math.abs(rectOf($('#canvas')).width - canvas0) < 1 && Math.abs(rectOf($('.verdict')).width - bar0) < 1 && Math.abs(rectOf(fig).left - before.left) < 1 && Math.abs(rectOf(fig).top - before.top) < 1, canvas0 + ' -> ' + rectOf($('#canvas')).width + '; bar ' + bar0 + ' -> ' + rectOf($('.verdict')).width);
      const cs = pane && w.getComputedStyle(pane);
      check('C2.5 @1280 the overlay floats over the canvas with a shadow and a close control', pane && (cs.position === 'fixed' || cs.position === 'absolute') && cs.boxShadow !== 'none' && rectOf(pane).width >= 280 && $('.insp-close') && rectOf($('.insp-close')).width > 0, pane && cs.position + ' / ' + cs.boxShadow.slice(0, 40));
      check('C2.5 @1280 the selected figure is not under the overlay', pane && !hit(rectOf(fig), rectOf(pane)), pane && JSON.stringify([rectOf(fig).left | 0, rectOf(fig).right | 0, rectOf(pane).left | 0, rectOf(pane).right | 0]));
      key(w, w.document.activeElement, 'Escape');
      await sleep(120);
      check('C2.5 @1280 Esc returns to the strip and focus to the figure', (!$('.insp-pane') || rectOf($('.insp-pane')).width === 0) && rectOf($('#inspector')).width < 80 && w.document.activeElement === fig, rectOf($('#inspector')).width + ' / ' + (w.document.activeElement && w.document.activeElement.className));
      // and a figure on the left half: the overlay may stay on the right; nothing moves either
      const left = $$('#canvas .fig').filter((f) => { const r = rectOf(f); return r.width > 0 && r.left < 500; })[0];
      left.scrollIntoView({ block: 'center' });
      await sleep(60);
      left.focus();
      left.click();
      await sleep(150);
      check('C2.5 @1280 a figure on the left is not covered either', $('.insp-pane') && !hit(rectOf(left), rectOf($('.insp-pane'))), '');
      $('.insp-close').click();
      await sleep(100);
      check('C2.5 @1280 the close control returns to the strip', rectOf($('#inspector')).width < 80, rectOf($('#inspector')).width);
    }
    w = await open('#/czr-full-credit-assessment/front', [1440, 900]);
    {
      const fig = $$('#canvas .fig')[0];
      fig.focus();
      fig.click();
      await sleep(100);
      const ip1440 = $('.insp-pane');
      check('C2.5 @1440 nothing changes: the inspector stays a docked 300px column (no overlay)', ip1440 && rectOf($('#inspector')).width === 300 && w.getComputedStyle(ip1440).position !== 'fixed' && w.getComputedStyle(ip1440).boxShadow === 'none', ip1440 ? w.getComputedStyle(ip1440).position : 'no .insp-pane');
    }
    for (const sz of [[1280, 800], [1440, 900]]) {
      w = await open('#/czr-full-credit-assessment/front', sz);
      // with the inspector open (the state in which the strip crowded at 1280: the canvas lost 264px to it)
      const f0 = $$('#canvas .fig').filter((f) => rectOf(f).width > 0)[0];
      f0.focus();
      f0.click();
      await sleep(150);
      const strip = $('.chart-slot[data-chart="chart.model_strip"]');
      strip.scrollIntoView({ block: 'center' });
      await sleep(60);
      const labs = $$('.chart-slot[data-chart="chart.model_strip"] svg text.ax.cx').map((t) => ({ r: rectOf(t), s: t.textContent })).filter((x) => x.r.width > 0);
      const bad = [];
      labs.forEach((a, i) => labs.forEach((b, j) => {
        if (j <= i || Math.abs(a.r.top - b.r.top) > 3) return;
        const gap = a.r.left < b.r.left ? b.r.left - a.r.right : a.r.left - b.r.right;
        if (gap < 10) bad.push(a.s + '/' + b.s + ' gap ' + Math.round(gap));
      }));
      check('C2.5 @' + sz[0] + ' (inspector open): the Model chart strip\u2019s x-axis labels never crowd (10px apart at least)', labs.length >= 3 && bad.length === 0, bad.slice(0, 4).join(' | ') + ' of ' + labs.map((x) => x.s).join(' '));
      const na = $$('.chart-slot[data-chart="chart.model_strip"] svg text.na');
      check('C2.5 @' + sz[0] + ': the n/a marks stay on the axis at their own category', na.length >= 2, na.length);
    }

    }

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
