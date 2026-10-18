"""CZR CP-5: evidence trace.

Module status and the citation counts are computed from the handoffs already built for the run (plan order: CP-5 runs
before CP-6 and CP-8, so those two are not assessed). The limitations are the real CAOS limitation flags and the Front
Pages' binding limitations for each module, plus the synthetic content the fixture adds. The findings are the cross-module
problems this fixture really has (for example the covenant-against-company EBITDA definition and the spread-benchmark
lineage), written as CP-5 would report them; the status words are the fixture's.

The real CAOS CP-5 (covenant run) was Ready with Remediation at confidence 16 of 100.
"""

from __future__ import annotations

from core import Ctx, Handoff
from czr.cp_3 import AS_OF, is_primary
from helpers import caos_text

FOLDER = "covenant-refinancing-2026-10-05"

# module -> (limitation, effect on the decision, source that would lift it)
LIMITS: dict[str, tuple[str, str, str]] = {
    "CP-0": (
        "Ratings outlooks, Fitch, issue ratings beyond the two 2032 notes and the merger debt terms are not in the Source Pack (G10, G11, G35, G8)",
        "Readiness is With limitations; the loans and other notes count as Unrated in Fit",
        "Agency reports and the merger commitment papers",
    ),
    "CP-1": (
        "No post-June financials, fewer than four complete discrete quarters, and no Q2 cash flows",
        "No quarterly cash conversion; the series stops at LTM Q2 2026",
        "Q1 and Q2 cash-flow statements and the next 10-Q",
    ),
    "CP-1A": (
        "No issuer or corporate family rating and no outlooks in the pack (G25, G11); the fixture's corporate ratings are synthetic",
        "Rating-linked judgements rest on test values",
        "Agency reports",
    ),
    "CP-1B": (
        "Cash flows are disclosed for six months only, so the cash side of the earnings delta is H1",
        "Cash conversion is not established quarterly",
        "Quarterly cash-flow statements",
    ),
    "CP-1C": (
        "The peer set is limited to MGM and PENN with no market capitalisation, EV or transaction comparables; EBITDAR definitions differ",
        "Positioning against peers is indicative",
        "A Sector RV Workbook and peer EV data",
    ),
    "CP-1D": (
        "The current operating lease liability is not disclosed and quality-adjusted EBITDA is unresolved",
        "Debt-like items are partly estimated",
        "The 30 June lease note",
    ),
    "CP-2": (
        "No post-June financials or complete credit agreement; the Credit Score, Direction and Sector Outlook are the module's illustrative words",
        "The credit view is not committee-ready",
        "A committee-ready run with supplied factor weights",
    ),
    "CP-2A": (
        "Current covenant headroom is not disclosed and the full credit agreement and collateral package are missing",
        "Downside paths have no numeric thresholds",
        "The compliance certificate and security documents",
    ),
    "CP-2D": (
        "The 12-month cash-flow bridge is incomplete and revolver fungibility and covenant headroom are unresolved",
        "Runway rests on mandatory uses before operating cash flow",
        "A 12-month cash forecast",
    ),
    "CP-2E": (
        "FX detail and hedge terms are limited and cost pass-through is unquantified",
        "Rate sensitivity is on unhedged variable debt only",
        "Hedge documents and a currency split",
    ),
    "CP-2G": (
        "No company guidance; the Base and Downside drivers are synthetic (G13)",
        "Projections are illustrations, not forecasts",
        "Management guidance or a lender model",
    ),
    "CP-2H": (
        "No agency-specific triggers or numeric forecast cases; thresholds are synthetic (G31)",
        "Headroom to a rating trigger is indicative",
        "Agency reports",
    ),
    "CP-3": (
        "No loan prices (G18), no benchmark curve (G19) and no Sector RV Workbook; Valuation, compensation and preference are illustrative",
        "The loans are valued on synthetic marks and spreads are proxies",
        "Loan marks, a benchmark curve and the Sector RV Workbook",
    ),
    "CP-3C": (
        "Current covenant headroom, basket usage and the full credit agreement are unavailable; the funding gap is cumulative scheduled maturities with no operating cash flow",
        "LME capacity is indicative and the gap is not a 12-month bridge",
        "The compliance certificate and a basket tracker",
    ),
    "CP-3D": (
        "Last trades only: no executable quotes, benchmark curve or bond analytics; the recovery assumption is a single synthetic 40%",
        "Implied hazards are illustrations and not default forecasts",
        "Two-sided quotes with size and a benchmark curve",
    ),
    "CP-4": (
        "The complete current credit agreement, intercreditor agreement and basket usage are absent; covenant EBITDA is not reconciled (G34); the restricted-payment and investment baskets are synthetic (G32)",
        "Headroom is on company Adjusted EBITDA and capacity is formula-only",
        "The full agreements and a compliance certificate",
    ),
    "CP-4C": (
        "The distress gate is not verifiable after 30 June and no claims, EV, waterfall or paths are constructed",
        "No recovery view exists for any class",
        "Q3 2026 results and current debt and covenant updates",
    ),
    "CP-5": (
        "Traceability is judged from citation counts and anchoring, not from re-reading every source line; the real CAOS evidence trace was Ready with Remediation at confidence 16 of 100",
        "The trace shows where provenance is thin, not that a figure is right",
        "A re-read of the top material drivers against their sources",
    ),
    "CP-6": (
        "The Recommendations, Valuations, thesis and challenge resolutions are the illustrative layer; the real CAOS runs never reached CP-6",
        "No Recommendation here is a committee decision",
        "A committee-ready run with a supplied mandate and factor weights",
    ),
    "CP-8": (
        "The prior Report is synthetic, except the LTM figures calculated from the filings; the Earnings Update plan has no CP-6, so no current Recommendation exists",
        "The comparison shows the Prior Case design, not a real earlier view",
        "A real earlier RBOT Report",
    ),
    "CP-DR": (
        "Fetched sources are synthetic and no fetched file exists; RQ3 is unanswered",
        "Research answers are test values, not evidence",
        "Running the fetch layer against the approved questions",
    ),
    "CP-L10": (
        "A screening module: the credit view words are illustrative and the structured outcome is FULL_UPGRADE_REQUIRED",
        "No Full-depth conclusion can be drawn",
        "The Full Pathway modules named in the upgrade triggers",
    ),
    "MODEL": (
        "The Model's EV is the merger transaction value through the Run Brief multiple; there is no listed equity value (G27)",
        "The EV multiple is the only EV input",
        "An equity value export",
    ),
    "PROJECTION": (
        "Drivers and the rate deck are synthetic (G13, G30)",
        "Projected leverage and liquidity are illustrations",
        "Management guidance and a forward curve",
    ),
    "FIT": (
        "The portfolios are synthetic and issue ratings for the loans and other notes are not in the pack (G35)",
        "Unrated instruments count in the CCC bucket and set thin headroom",
        "Real mandates and issue ratings",
    ),
}


def _counts(hd: Handoff) -> tuple[int, int]:
    syn = sum(1 for c in hd.citations if c["synthetic"])
    return len(hd.citations) - syn, syn


def _traceability(real: int, syn: int, blocked: bool) -> str:
    """Untraceable when nothing was admitted, Partly traceable when any citation is synthetic, else Traceable."""
    if blocked or real + syn == 0:
        return "Untraceable"
    return "Traceable" if syn == 0 else "Partly traceable"


def build(ctx: Ctx, run_id: str, variant: str) -> Handoff:
    h = Handoff(ctx, "CP-5", "CZR", run_id, AS_OF, ["CP-0"], fixture_file="czr/cp_5.py")
    h.qa("Restricted")
    built = {
        step: hd
        for (rid, step), hd in ctx.built.items()
        if rid == run_id and step not in ("RUN_BRIEF", "CP-5")
    }
    h.inputs = list(dict.fromkeys(["CP-0"] + list(built)))
    syn_cite = h.cite_synthetic(
        "cp5",
        "The status counts are computed from this fixture's handoffs, and the findings describe real inconsistencies between its modules.",
        "Caesars",
        file="czr/cp_5.py",
    )

    # ---- module status
    status_rows = []
    for step, hd in built.items():
        real, syn = _counts(hd)
        blocked = hd.qa_status == "Blocked"
        if step == "FIT":  # a host step: computed from the portfolio file, which is synthetic here
            trace, note = (
                "Partly traceable",
                "computed by the host step from the CP-1 identities and the portfolio files, which are synthetic",
            )
        else:
            trace = _traceability(real, syn, blocked)
            note = f"{real} real and {syn} synthetic citations" + (
                "; no content admitted" if blocked else ""
            )
        status_rows.append(
            {"module_id": step, "qa_status": hd.qa_status, "traceability": trace, "note": note}
        )
    h.table("cp5.module_status", status_rows)

    # ---- limitations: one per assessed module that is not Pass
    lim_rows = []
    for step, hd in built.items():
        if hd.qa_status == "Pass":
            continue
        lim, eff, lift = LIMITS[step]
        if hd.qa_status == "Blocked":
            lim = "Blocked: no market observation was admitted, so every table is blank. " + lim
            eff = "The spread curve and implied-PD charts are n/a; " + eff
        lim_rows.append(
            {
                "module_id": step,
                "limitation": lim,
                "effect_on_decision": eff,
                "source_that_would_lift": lift,
            }
        )
    # the modules that run after CP-5 (and CP-5 itself) are named too, so none is left unnamed
    hdr = ctx.get(run_id, "RUN_BRIEF").rows("snapshot.run_header")[0]
    plan = ctx.spec["pathways"][hdr["pathway"]]["depths"][hdr["depth"]]
    prior = bool(ctx.get(run_id, "RUN_BRIEF").rows("brief.prior_case"))
    for step in ["CP-5"] + [m for m in plan[plan.index("CP-5") + 1 :] if m != "CP-8" or prior]:
        lim, eff, lift = LIMITS[step]
        lim_rows.append(
            {
                "module_id": step,
                "limitation": lim,
                "effect_on_decision": eff,
                "source_that_would_lift": lift,
            }
        )
    h.table("cp5.limitations", lim_rows)

    # ---- findings: only those that apply to the modules present
    findings: list[tuple] = []

    def add(sev, mod, kind, desc, fix, status):
        findings.append((sev, mod, kind, desc, fix, status))

    if "CP-4" in built:
        add(
            "Medium",
            "CP-4",
            "Consistency",
            "Covenant headroom is computed on company LTM Adjusted EBITDA and face debt, while the covenants use their own EBITDA and Total Net Debt definitions; CP-1 and CP-4 do not reconcile the two (G34).",
            "Reconcile the covenant EBITDA to Adjusted EBITDA or label every headroom figure as RBOT-basis.",
            "Open",
        )
        add(
            "Medium",
            "CP-4",
            "Lineage",
            "The restricted-payment and investment basket sizes and usage in the capacity register are synthetic (G32); the real extraction found only the formulas.",
            "Replace with the extracted baskets and a basket tracker.",
            "Accepted",
        )
    if "CP-3D" in built and built["CP-3D"].qa_status != "Blocked":
        add(
            "Medium",
            "CP-3D",
            "Market",
            "The fund's 30 June valuation of the secured 2032s is a Stale evaluated price, 4.34 points above the 1 October last trade; it is kept as an observation but carries no spread.",
            "Refresh with a dated two-sided quote.",
            "Accepted",
        )
    elif "CP-3D" in built:
        add(
            "High",
            "CP-3",
            "Consistency",
            "CP-3D admitted no market observation, yet CP-3 reads the same TRACE pages as Market levels; the two modules disagree on what counts as admitted evidence.",
            "Align the admission rule or mark the CP-3 levels as unadmitted.",
            "Open",
        )
    if "CP-3" in built:
        add(
            "Medium",
            "CP-3",
            "Lineage",
            "Spread columns use a synthetic 6-year Treasury of 4.10% and the term-loan marks are synthetic dealer quotes (G18, G19), so spreads and discount margins are proxies.",
            "Supply a benchmark curve and loan marks.",
            "Accepted",
        )
    if "CP-3C" in built:
        add(
            "Medium",
            "CP-3C",
            "Consistency",
            "The funding gap uses the 10-Q annual maturity schedule, which includes amortisation (767 in 2028), while the Model's maturity wall is by final maturity (739 in 2028); the two measures differ on the same Front Page.",
            "State the basis on both views or add amortisation to the wall.",
            "Open",
        )
    if "CP-1A" in built:
        add(
            "Low",
            "CP-1A",
            "Lineage",
            "The corporate family rating and outlooks are synthetic (no agency report is in the pack).",
            "Supply the agency reports.",
            "Accepted",
        )
    if "CP-2" in built:
        add(
            "Low",
            "CP-2",
            "Lineage",
            "Credit Score, Credit Direction and Sector Outlook are the module's illustrative words, cited to a synthetic row.",
            "Replace with a committee-ready run.",
            "Accepted",
        )
    if "CP-L10" in built:
        add(
            "Low",
            "CP-L10",
            "Lineage",
            "The credit-view words at Screening basis repeat the illustrative view; the real LITE run assigned none.",
            "Run the Full Pathway.",
            "Accepted",
        )
    if is_primary(ctx, run_id) and "CP-1" in built:
        add(
            "Medium",
            "CP-1",
            "Lineage",
            "The three merger tranches, their pro forma debt and interest are synthetic (G8), so PF-LTM leverage and cover rest on test values.",
            "Replace with the commitment papers.",
            "Accepted",
        )
    if "CP-1B" in built:
        add(
            "Low",
            "CP-1B",
            "Consistency",
            "Cash flows are disclosed for six months only, so the H1 cash conversion in CP-1D cannot be compared with the Q2 earnings delta in CP-1B.",
            "Add the Q1 and Q2 cash-flow statements.",
            "Open",
        )
    if "CP-1D" in built:
        add(
            "Medium",
            "CP-1D",
            "Consistency",
            "The operating lease liability is stated at 31 December 2025 but not at 30 June 2026 (G5), so adjusted debt mixes two balance-sheet dates.",
            "Obtain the 30 June lease note or label the date on the debt-like items.",
            "Open",
        )
    if "CP-DR" in built:
        add(
            "Medium",
            "CP-DR",
            "Lineage",
            "The four fetched sources are synthetic and no fetched file exists, so research answers RQ1 and RQ2 rest on test values; RQ3 is unanswered.",
            "Run the fetch layer against the approved questions.",
            "Accepted",
        )
    if "PROJECTION" in built:
        add(
            "Low",
            "PROJECTION",
            "Calculation",
            "Base and Downside drivers and the rate deck are synthetic (G13, G30); the projection identities hold but the inputs are illustrations.",
            "Supply guidance and a forward curve.",
            "Accepted",
        )
    h.table(
        "cp5.findings",
        [
            {
                "finding_id": f"F-{i:02d}",
                "severity": sev,
                "module_id": mod,
                "kind": kind,
                "description": desc,
                "required_fix": fix,
                "status": st,
            }
            for i, (sev, mod, kind, desc, fix, st) in enumerate(findings, 1)
        ],
    )

    # ---- analysis
    cc = lambda s: caos_text(h, FOLDER, "CP-5", s)  # noqa: E731
    n_syn = sum(1 for hd in built.values() for c in hd.citations if c["synthetic"])
    n_all = sum(len(hd.citations) for hd in built.values())
    n_r = sum(1 for r in status_rows if r["qa_status"] == "Restricted")
    n_b = sum(1 for r in status_rows if r["qa_status"] == "Blocked")
    sev = {k: sum(1 for f in findings if f[0] == k) for k in ("High", "Medium", "Low")}
    paras = [
        "The analysis is traceable enough to design from but not to decide on: every figure cites a source, yet the evidence is thin where it matters most. "
        + cc(
            "The real CAOS evidence trace was Ready with Remediation at confidence 16 of 100: of the five material drivers, three were directly sourced and two were insufficient, and the most important gap was current, instrument-specific refinancing-market evidence, with the full merger financing terms also unavailable. {12, 13, 14}"
        ),
        f"Across the {len(status_rows)} assessed handoffs, {n_r} are Restricted and {n_b} Blocked; of {n_all} citations, {n_syn} are synthetic and say so in their source. {syn_cite} "
        f"CP-5 raises {len(findings)} findings: {sev['High']} High, {sev['Medium']} Medium and {sev['Low']} Low.",
        "The findings that matter are cross-module. "
        + (
            "Covenant headroom is on company Adjusted EBITDA while the covenants use their own definitions, so every headroom figure is indicative. "
            if "CP-4" in built
            else ""
        )
        + (
            "The funding gap and the Model's maturity wall measure different things (scheduled maturities against final maturities). "
            if "CP-3C" in built
            else ""
        )
        + "Spread and discount-margin columns rest on a synthetic benchmark and synthetic loan marks. None changes a figure's arithmetic, which the validator checks; they limit what the figures can be used for.",
        cc(
            "Reported compliance with the financial covenants and positive Regional EBITDA are the offsets to a thin trace, but neither supplies a covenant certificate, a lender indication or a market price. {16}"
        )
        + " What would change this view: the compliance certificate, the merger commitment papers and dated two-sided quotes would lift the three largest provenance gaps. Confidence in this module: Low.",
    ]
    h.analysis("\n\n".join(paras))
    h.gaps(
        "- CP-6 and CP-8 run after CP-5 in the plan and are not assessed here. Lifted by: a post-run trace.\n"
        "- Traceability is judged from citation counts and anchoring, not from re-reading each source line; the mechanical checks are the validator's.\n"
        "- The status counts include the fixture's synthetic citations; a real run would have none of them."
    )
    return h
