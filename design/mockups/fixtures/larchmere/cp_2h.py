"""Larchmere CP-2H: ratings migration and triggers. Blocked: no rating-agency report was admitted, so the agencies'
trigger thresholds are unknown; the tables are kept with critical cells blank and the gaps say why."""

from __future__ import annotations

from core import GAP, Ctx, Handoff

from . import facts as F
from .facts import syn


def build(ctx: Ctx, run_id: str, variant: str) -> Handoff:
    h = Handoff(
        ctx,
        "CP-2H",
        F.ISSUER_ID,
        run_id,
        F.AS_OF,
        ["CP-0", "CP-1A", "MODEL"],
        fixture_file="larchmere/cp_2h.py",
    )
    h.qa("Blocked")
    rat = F.val("ratings")
    m_rat = syn(h, "ratings")
    h.table(
        "cp2h.rating_triggers",
        [
            {
                "agency": "Moody's",
                "rating_type": "Corporate family rating",
                "direction": GAP,
                "metric": GAP,
                "unit_label": GAP,
                "threshold": GAP,
                "current_value": GAP,
                "projected_value": GAP,
                "headroom": GAP,
                "status": GAP,
                "cite": GAP,
            },
            {
                "agency": "S&P",
                "rating_type": "Issuer credit rating",
                "direction": GAP,
                "metric": GAP,
                "unit_label": GAP,
                "threshold": GAP,
                "current_value": GAP,
                "projected_value": GAP,
                "headroom": GAP,
                "status": GAP,
                "cite": GAP,
            },
        ],
    )
    h.table(
        "cp2h.migration_view",
        [
            {
                "agency": a,
                "case": c,
                "likely_transition": GAP,
                "earliest_timing": GAP,
                "catalyst": GAP,
                "confidence": GAP,
                "cite": GAP,
            }
            for a in ("Moody's", "S&P")
            for c in ("BASE", "DOWNSIDE")
        ],
    )
    h.analysis(
        f"The pack cannot say which rating trigger is nearest or when, so this module is Blocked. What is evidenced is the pressure itself: Moody's lowered the corporate family rating to {rat['moodys'][0]} from {rat['moodys'][3]} on {rat['moodys'][2]}, "
        f"and S&P lowered the issuer credit rating to {rat['sp'][0]} from {rat['sp'][3]} on {rat['sp'][2]}, both with negative outlooks {m_rat}.\n\n"
        "No agency report was admitted to the Source Pack, so the agencies' stated downgrade thresholds, their leverage and coverage metrics and any timing language are unknown. "
        "Without them there is no threshold against which to compute headroom, and inventing one would present a guess as an extraction. The trigger and migration tables therefore keep their rows and leave every value blank.\n\n"
        "As an analyst view, not an extraction: both agencies typically move to a default-category rating when a coupon is unpaid beyond its grace period. If the 15 October 2026 grace period lapses the next action is probably a downgrade to default, which would be a trigger event for any rating-linked covenants and investor mandates. "
        "Confidence in this module is not assessed."
    )
    h.gaps(
        "- Rating triggers (downgrade and upgrade thresholds, metrics, current and projected values, headroom): no rating-agency report admitted, so the thresholds are unknown. Effect: no rating-trigger headroom or bullet chart values. Lifted by: a Moody's or S&P rating report or press release.\n"
        "- Migration timing and catalysts: no agency commentary admitted. Effect: the likely transition and earliest timing are blank for both agencies and both cases. Lifted by: the same reports.\n"
        "- Cites: the ratings themselves are cited in CP-1A's ratings register and in this module's analysis; the table rows cite nothing because they contain no extracted value."
    )
    h.analysis_md, h.gaps_md = F.prose(h.analysis_md), F.prose(h.gaps_md)
    return h
