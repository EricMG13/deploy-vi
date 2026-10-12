# Mutation record — the Model

Historical baseline (before these review fixes): `bash scripts/mutate_model.sh` (mutmut 3.7.0) on `rbotlib/model/`, 2026-10-11: 9424 mutants, 9243 killed, 3 timed out (killed), 178 survived. Every survivor is below, by why it is not killed; a survivor of a later run that is not listed is a test gap to kill, never an entry to add. Entries read `` `<module>.<function>` <mutant numbers> `` (mutmut's `rbotlib.model.<module>.x_<function>__mutmut_<n>`).

- **P** (19), reachable only with projected columns or a rate deck: the unallocated line's parts and total, the projected interest bridge, the deck date (Plan 13 brings back caos's projection tests, which reach them): `assemble._interest_closes` 10, 11, 19, 25; `layout._debt_specs` 13, 14, 15, 18, 27, 34, 35; `layout._specs` 70; `layout._unallocated` 2, 3, 10, 11, 14, 22; `layout.layout` 48.
- **E1** (4), dividing by a sign of +1 or -1 multiplies by it: `_cells.calc` 19; `assemble._sum` 8, 13; `metrics._total` 7.
- **E2** (15), `zip(..., strict=...)` over sequences the code already makes equal in length: `assemble._limitations` 4, 7, 8; `output._line` 46, 49, 50; `output._rows` 4, 7, 8; `reader.rows` 30, 33, 34; `run._rows` 4, 7, 8.
- **E3** (9), UTF-8 spelled `UTF-8`, or the platform default, which is UTF-8 on the work machine and macOS: `run.read_handoff` 4, 6, 17; `run.run_model` 202, 204, 210, 216, 218, 227.
- **E4** (7), `closed=None` is as falsy as `closed=False`: `house_inputs._debt_like` 5; `house_inputs._equity` 36; `house_inputs.check_entity_profile` 17; `inputs._facility` 5, 98; `inputs._kpi` 45; `inputs._period` 52.
- **E5** (5), `format(x, "F")` and `format(x, "f")` print a finite Decimal alike: `layout._decimal_text` 6; `output._decimal` 5, 7; `snapshot.display` 17, 19.
- **E6** (10), a path differing only in letter case: macOS file systems ignore case (a case-sensitive file system kills these through the same tests): `run.run_model` 6, 14, 19, 21, 22, 207, 214, 222, 224, 225.
- **E7** (9), argparse help text: `run.add_command` 3, 5, 8, 9, 10, 14, 18, 24, 25.
- **E9** (3), `\N{em dash}` and `\N{EM DASH}` name the same character: `house_inputs._identity` 17; `run.run_model` 155, 165.
- **E10** (18), `display` formats a money amount and an unknown unit alike (only multiples, percentages and days are rounded): `run._analysis` 7, 13, 14, 17, 23, 24; `snapshot._adjustment_row` 22, 25, 26; `snapshot._total_row` 2, 5, 6; `snapshot.capital_structure` 34, 37, 38; `snapshot.maturity_wall` 18, 21, 22.
- **E11** (1), the slug is case-folded first, so stripping `X` as well as `_` strips nothing more: `house._slug` 7.
- **E12** (4), `calc` takes no basis from its parts, so the parts' basis is never read: `house._adjusted_debt` 10, 12, 13, 14.
- **E13** (4), the mixed-separator branches refuse every figure on which `find` and `rfind` differ: `reader._separated` 4, 11, 13, 15.
- **E14** (1), both sides of the vocabulary match go through `_key`, so any separator spelling matches alike: `reader._key` 5.
- **E15** (4), a four-digit end year falls back to the last four-digit run, which is the same year: `reader._end_year` 4, 7, 8, 9.
- **E16** (3), the fiscal-period key is compared only with other keys from the same function: `inputs._fiscal_period` 6, 7, 8.
- **E17** (1), `ensure_ascii=None` is as falsy as `False`: `output.dumps` 4.
- **E18** (3), the display context: the default context also rounds half-even, and a display figure has far fewer than 28 digits: `snapshot.display` 2, 10, 12.
- **E19** (4), a cell for a missing column is shown as a gap whatever its reason: `snapshot.shown_cell` 2, 4, 5, 6.
- **E20** (2), a PF-LTM column's kind is `PF_LTM` either way: `snapshot.financial_columns` 15, 16.
- **E21** (1), the last two lines of the Model are both in band 12: `snapshot.metrics` 24.
- **E22** (7), the Equity basis label for a missing EV basis is the gap either way; `shown` other than `debt` or `share` prints no multiple, as `amount` does: `snapshot.capital_structure_totals` 91, 153, 165, 166, 200, 212, 213.
- **E23** (5), a payment rank is set on every facility line, so the no-rank cell is never built: `snapshot.capital_structure` 17, 18, 19, 20, 21.
- **E24** (1), maturity rows are unique by (year, facility), so sorting by the whole row orders them alike: `snapshot.maturity_wall` 24.
- **E25** (1), the notes map's values are never read, only its keys: `assemble._limitations` 10.
- **E26** (2), the debt band's first line is always a facility, a rank subtotal or the unallocated line, each of which sets `counted` before it is read (and `None` is as falsy as `False`): `assemble._summed` 2, 3.
- **E27 corrected (2026-10-12):** `assemble.credit_model` 63, 64, 75 are killable on mixed segment types. `test_assemble_guards.test_a_segment_corporate_in_any_row_has_no_growth` distinguishes NOT_APPLICABLE from ZERO_OR_NEGATIVE_DENOMINATOR; they are removed from the equivalent list and included in the current money rerun below.
- **E28** (2), without an opening day there is no opening stack to check against; a facility with a row ending on the opening day is in the opening stack either way: `debt._issued_after` 4, 13.
- **E29** (5), the sparse cover's `tiled` flag is read only together with a figure for the parts, which these paths never have; past the last period start the cover ends either way; `""` is as falsy as `None`: `history._cover` 4, 21, 32; `history._parts` 6; `history._step` 25.
- **E30** (3), a subtotal reads its parts, never its key; every part of a rank subtotal is a facility key with the same missing reason; summing Decimals from an int 0 gives the same Decimal: `layout._rank_specs` 24; `layout._revenue_cell` 11; `layout._subtotal` 13.
- **E31** (1), a one-day span is never a whole month, so tightening the bounds check changes no result: `periods._whole_months` 7.
- **U** (21), unreachable defensive branch: the input that reaches it cannot occur (every Model notes `NO_PROJECTIONS`; every looked-up line exists; openpyxl always returns a worksheet; parsed cells hold no line break; units are a closed vocabulary): `output._markdown` 2, 4; `output.model_md` 34, 35, 36; `snapshot.financials` 14, 15, 16, 17; `snapshot.line_of` 3; `snapshot.money_label` 2, 4, 5; `snapshot.summary` 30; `snapshot.unit_label` 21, 22, 23, 24, 28; `xlsx._sheet` 4, 5.

## Earlier review-fix money run — 2026-10-12 (Codex; historical after final-review repairs)

Selected `house`, `house_inputs`, `metrics`, `periods`, `history`, `assemble`: 3761 actual mutants; 3725 killed, 4 timeout, 32 survive after rerunning the 78 reached survivors with strengthened tests (46 newly killed). The source-path workspace mirrors `scripts/mutate_model.sh` and restricts `only_mutate` to those six files; no production calculation changed during the survivor repair. New assertions cover causal computed interest, exact zero/subunit EV and annual endpoints, current-LTM status selection, names/reasons and undated balances. E27 63/64/75 are killed.

Current survivors, exhaustively (numbers are local to this run; historical ids above need not remain stable):
- `house._on` 12: a missing key's sentinel `XXXX` cannot equal a parsed ISO date or None, as the original empty string cannot.
- `house._adjusted_debt` 10,12,13,14: E12, part basis is not read by calc.
- `house._above_structuring` 22: replacing fallback 0 with 1 keeps None/zero non-negative; negative values do not take the fallback.
- `house_inputs.debt_like_key` 7: uppercase X cannot occur after casefold; stripping X as well as underscore is unchanged.
- `house_inputs._identity` 17: E9, Unicode character-name case; `_equity` 36, `check_entity_profile` 17, `_debt_like` 5: E4, None remains falsy.
- `metrics._total` 7; `assemble._sum` 8,13: E1, finite Decimal division by sign ±1 equals multiplication.
- `history._parts` 6, `_cover` 4,21,32, `_step` 25: E29, unused tiled flag, equivalent end-of-cover and falsy-note branches.
- `assemble._limitations` 4,7,8: E2, equal-length generated sequences; 10: E25, only note-map keys are read.
- `assemble._summed` 2,3: E26, counted initialized by every first debt-band line and None remains falsy.
- `assemble._interest_closes` 10,11,19,25: P, only projected columns/rate decks (Plan 13); unreachable from current historical inputs.
- `periods._whole_months` 7: E31, one-day span yields no whole month either way; `_host_ltm` 25,26: FY term days equal anchor day_count, so taking term-days fallback is unchanged.

Timeouts: `house.house_view` 305 (framework timeout); `history._cover` 30,38 and `_next_start` 5 (loop mutations consuming CPU beyond eight minutes, bounded owned children with SIGXCPU). Timeout identities and native logs retained in scratch. Whole-current-package mutation coverage and Plan 13 projections are not verified; the earlier whole-package result is historical only.

## Final-review repair selection — 2026-10-12 (Codex)

Fresh actual selection: `house._dates`, `house._on`, `inputs._span`, `snapshot._adjustment_row`: 101 mutants, 100 killed, 0 timeout, 1 survivor. The workspace generated3129 mutants in these three files but3028 were not selected or tested; this is not a whole-file/package result. Rerunning only6 reached survivors killed5 through stronger unknown-date and money-unit carrier assertions, with actual mutant RED and production GREEN. Earlier six-file/whole-package results above are historical after these source repairs.

Only survivor: `house._on`12 (missing-key sentinel empty string→XXXX). Actual generated function compared with production across24 pairs: dated/undated/missing registered keys, valid ISO/None column dates, Debt-like/Unclear treatment; all amounts/membership equal. Neither sentinel can equal a validated ISO date or None; missing registry dates remain excluded. Native evidence and actual-generated AST probe are retained under scratch `p03-codex/final-review-repair/`. Caller-wiring changes are covered by focused/typed/full tests; they are not a broader mutation claim.
