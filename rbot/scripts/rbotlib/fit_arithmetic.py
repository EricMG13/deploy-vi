"""Portfolio Fit arithmetic (interfaces spec section 7), pure Decimal with no I/O.

For one portfolio (`prepared/portfolios/<id>.json`) and one instrument:

1. `current_exposure` = the par of the portfolio's positions in the run's issuer;
   `current_exposure_pct_nav` = that / NAV x 100.
2. The limits the instrument touches: every `issuer` limit, whose current value is the run
   issuer's own exposure in the limit's unit (the file's figure is its largest obligor); a
   `sector`, `country`, `rating_bucket`, `asset_type`, `seniority`, `maturity` or `currency`
   limit when its `scope_value` names the instrument's attribute, or when it has none (a
   "largest bucket" limit, whose current value bounds every bucket). Headroom is the limit
   less the current value in the limit's unit (for a maturity limit in years, the limit less
   the instrument's tenor); `headroom_amount` converts it to the run's currency and unit
   (`pct_nav` x NAV / 100, `pct_par` x par / 100, `amount` as is); a count or a maturity limit
   does not cap the size (`headroom_amount` None). A touched limit is `Not computed` when the
   instrument's attribute it needs is missing, or the portfolio's currency is not the run's.
   An `other` limit (a book statistic such as top-10 concentration or WAL) is shown `From file`
   and never binds.
3. `max_size` = the smallest `headroom_amount` over the computed Hard limits, floored at 0;
   `binding_limit` is the limit giving it (none when no Hard limit caps the size).
4. `verdict`: `Breaches` when a Hard limit has negative headroom or `max_size` is 0; `Watch`
   when a Soft limit has negative headroom, `max_size` is under 1% of NAV, or a touched limit
   is `Not computed`; otherwise `Fits`.
5. `recommendation_cap`: `Breaches` -> `Avoid`, `Watch` -> `3 - MW`, `Fits` -> `1 - Strong OW`
   (no cap).

Limits `rbot prepare` could not read into a maximum (minimum limits, info-only rows) are in
the portfolio's `unparsed` list; Portfolio Fit does not size against them and the FIT
Handoff names each under `## Gaps`.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from datetime import date
from decimal import ROUND_HALF_EVEN, Context, Decimal
from typing import Any

CONTEXT = Context(prec=38, rounding=ROUND_HALF_EVEN)
HUNDRED = Decimal(100)
DAYS_PER_YEAR = Decimal(365)
WATCH_SHARE_OF_NAV = Decimal("0.01")
FITS, WATCH, BREACHES = "Fits", "Watch", "Breaches"
CAP = {FITS: "1 - Strong OW", WATCH: "3 - MW", BREACHES: "Avoid"}
WITHIN, BREACHED, NOT_COMPUTED, FROM_FILE = "Within", "Breached", "Not computed", "From file"
SCOPES = ("sector", "country", "rating_bucket", "asset_type", "seniority", "maturity", "currency")
_SCALE = {"UNITS": Decimal(1), "THOUSANDS": Decimal(1000), "MILLIONS": Decimal(1_000_000)}
_LOANS = frozenset({"RCF", "1L Term Loan", "2L Term Loan", "DIP Financing"})
_BONDS = frozenset({"SS Notes", "SU Notes", "Sub Debt", "PIK", "Hybrid"})
_SENIOR = frozenset({"RCF", "1L Term Loan", "SS Notes", "DIP Financing"})
_JUNIOR_WORDS = ("unsecured", "2nd lien", "second lien", "subordinated", "junior")
_SENIOR_WORDS = ("1st lien", "first lien", "senior secured")
_MOODYS = (("Baa3", "IG"), ("Ba3", "BB"), ("B3", "B"))
_MOODYS_ORDER = (
    "Aaa Aa1 Aa2 Aa3 A1 A2 A3 Baa1 Baa2 Baa3 Ba1 Ba2 Ba3 B1 B2 B3 Caa1 Caa2 Caa3 Ca C"
).split()
_SP_ORDER = "AAA AA+ AA AA- A+ A A- BBB+ BBB BBB- BB+ BB BB- B+ B B- CCC+ CCC CCC- CC C D".split()
BUCKETS = ("IG", "BB", "B", "CCC")


@dataclass(frozen=True, slots=True)
class Instrument:
    facility_id: str
    name: str
    debt_type: str | None
    secured: bool | None
    currency: str | None
    maturity: date | None
    ratings: tuple[str, ...]  # agency ratings as written, missing ones left out
    sector: str | None
    country: str | None


@dataclass(frozen=True, slots=True)
class Portfolio:
    portfolio_id: str
    name: str
    strategy: str
    nav: Decimal
    par: Decimal
    currency: str
    unit: str
    positions: tuple[Mapping[str, Any], ...]
    limits: tuple[Mapping[str, Any], ...]


@dataclass(frozen=True, slots=True)
class Headroom:
    limit: Mapping[str, Any]
    current_value: Decimal | None
    headroom: Decimal | None
    headroom_amount: Decimal | None  # in the run's unit; None: does not cap the size
    status: str


@dataclass(frozen=True, slots=True)
class Fit:
    portfolio: Portfolio
    instrument: Instrument
    current_exposure: Decimal
    current_exposure_pct_nav: Decimal
    rows: tuple[Headroom, ...]
    max_size: Decimal | None  # None: no Hard limit caps the size
    binding_limit: str | None
    verdict: str
    reason: str
    currency: str  # of current_exposure and max_size: the run's, else the portfolio's
    unit: str

    @property
    def recommendation_cap(self) -> str:
        return CAP[self.verdict]


# --- instrument attributes -------------------------------------------------------------------


def rating_bucket(ratings: Sequence[str]) -> str:
    """The lowest bucket over the agencies' ratings (IG, BB, B, CCC); `Unrated` with none."""
    found = [b for b in (_bucket(r) for r in ratings) if b is not None]
    if not found:
        return "Unrated"
    return max(found, key=BUCKETS.index)


def _bucket(rating: str) -> str | None:
    text = rating.strip().rstrip("*").strip()
    if text in _MOODYS_ORDER:
        rank = _MOODYS_ORDER.index(text)
        return next((b for edge, b in _MOODYS if rank <= _MOODYS_ORDER.index(edge)), "CCC")
    if text in _SP_ORDER:
        rank = _SP_ORDER.index(text)
        edges = (("BBB-", "IG"), ("BB-", "BB"), ("B-", "B"))
        return next((b for edge, b in edges if rank <= _SP_ORDER.index(edge)), "CCC")
    return None


def asset_type(debt_type: str | None) -> str | None:
    if debt_type in _LOANS:
        return "Loan"
    return "Bond" if debt_type in _BONDS else None


def is_senior_secured(instrument: Instrument) -> bool | None:
    if instrument.debt_type in _SENIOR:
        return True
    if instrument.debt_type in _BONDS or instrument.debt_type == "2L Term Loan":
        return False
    return instrument.secured


def tenor_years(instrument: Instrument, as_of: date) -> Decimal | None:
    if instrument.maturity is None:
        return None
    return CONTEXT.divide(Decimal((instrument.maturity - as_of).days), DAYS_PER_YEAR)


# --- limits ----------------------------------------------------------------------------------


def _words(scope_value: str) -> list[str]:
    return [w.strip().casefold() for w in scope_value.split(",") if w.strip()]


def _seniority_match(scope_value: str, senior: bool | None) -> bool | None:
    text = scope_value.casefold()
    if any(w in text for w in _JUNIOR_WORDS):
        return None if senior is None else not senior
    if any(w in text for w in _SENIOR_WORDS):
        return senior
    return False


def touches(limit: Mapping[str, Any], instrument: Instrument) -> bool | None:
    """Whether the limit applies to the instrument; None when the attribute is missing."""
    scope, raw = limit["scope"], limit.get("scope_value")
    if scope == "issuer":
        return True
    if scope not in SCOPES:
        return False
    if raw is None:
        return True
    value = str(raw)
    if scope == "seniority":
        return _seniority_match(value, is_senior_secured(instrument))
    if scope == "maturity":
        return True if instrument.maturity is not None else None
    attribute = {
        "sector": instrument.sector,
        "country": instrument.country,
        "currency": instrument.currency,
        "asset_type": asset_type(instrument.debt_type),
        "rating_bucket": rating_bucket(instrument.ratings),
    }[scope]
    if attribute is None:
        return None
    return attribute.casefold() in _words(value)


def exposure(portfolio: Portfolio, issuer_id: str) -> Decimal:
    """Par of the portfolio's positions in the issuer."""
    with_issuer = [p for p in portfolio.positions if p.get("issuer_id") == issuer_id]
    return sum((Decimal(str(p["par"])) for p in with_issuer), Decimal(0))


def _issuer_current(unit: str, held: Decimal, portfolio: Portfolio, count: int) -> Decimal | None:
    """The run issuer's exposure in the limit's unit (portfolio units for an amount)."""
    if unit == "pct_nav":
        return CONTEXT.divide(held * HUNDRED, portfolio.nav)
    if unit == "pct_par":
        return CONTEXT.divide(held * HUNDRED, portfolio.par)
    if unit == "amount":
        return held
    return Decimal(count) if unit == "count" else None


def amount(headroom: Decimal, unit: str, portfolio: Portfolio, scale: Decimal) -> Decimal | None:
    """Headroom in the run's unit; None for a count or maturity limit (it caps no size)."""
    if unit == "pct_nav":
        return CONTEXT.multiply(CONTEXT.divide(headroom * portfolio.nav, HUNDRED), scale)
    if unit == "pct_par":
        return CONTEXT.multiply(CONTEXT.divide(headroom * portfolio.par, HUNDRED), scale)
    if unit == "amount":
        return CONTEXT.multiply(headroom, scale)
    return None


@dataclass(frozen=True, slots=True)
class Run:
    issuer_id: str
    as_of: date
    currency: str
    unit: str


def _scale(portfolio: Portfolio, run: Run) -> Decimal | None:
    """The factor from the portfolio's unit to the run's; None when currencies differ."""
    if portfolio.currency != run.currency:
        return None
    if portfolio.unit not in _SCALE or run.unit not in _SCALE:
        return None
    return CONTEXT.divide(_SCALE[portfolio.unit], _SCALE[run.unit])


def headroom_row(
    limit: Mapping[str, Any], instrument: Instrument, portfolio: Portfolio, run: Run
) -> Headroom | None:
    """The limit's row for the instrument, or None when it does not touch it."""
    if limit["scope"] == "other":
        stated = Decimal(str(limit["current_value"]))
        room = CONTEXT.subtract(Decimal(str(limit["limit_value"])), stated)
        return Headroom(limit, stated, room, None, FROM_FILE)
    touched = touches(limit, instrument)
    if touched is False:
        return None
    current = _current(limit, instrument, portfolio, run)
    scale = _scale(portfolio, run)
    if touched is None or current is None or scale is None:
        return Headroom(limit, current, None, None, NOT_COMPUTED)
    room = CONTEXT.subtract(Decimal(str(limit["limit_value"])), current)
    status = BREACHED if room < 0 else WITHIN
    return Headroom(limit, current, room, amount(room, limit["unit"], portfolio, scale), status)


def _current(
    limit: Mapping[str, Any], instrument: Instrument, portfolio: Portfolio, run: Run
) -> Decimal | None:
    if limit["scope"] == "issuer":
        held = exposure(portfolio, run.issuer_id)
        count = sum(1 for p in portfolio.positions if p.get("issuer_id") == run.issuer_id)
        return _issuer_current(limit["unit"], held, portfolio, count)
    if limit["scope"] == "maturity":
        return tenor_years(instrument, run.as_of)
    return Decimal(str(limit["current_value"]))


# --- the fit ---------------------------------------------------------------------------------


def _max_size(rows: Sequence[Headroom]) -> tuple[Decimal | None, str | None]:
    """The smallest computed Hard headroom amount, floored at 0, and its limit."""
    capped = [
        (r.headroom_amount, str(r.limit["limit_id"]))
        for r in rows
        if r.limit["limit_kind"] == "Hard" and r.headroom_amount is not None
    ]
    if not capped:
        return None, None
    size, limit_id = min(capped, key=lambda pair: pair[0])
    return max(Decimal(0), size), limit_id


def verdict(rows: Sequence[Headroom], max_size: Decimal | None, nav: Decimal) -> tuple[str, str]:
    """(verdict, reason) by the section 7 order: Breaches, then Watch, then Fits."""
    hard_breach = [r for r in rows if r.status == BREACHED and r.limit["limit_kind"] == "Hard"]
    if hard_breach:
        return BREACHES, f"hard limit {hard_breach[0].limit['limit_id']} has negative headroom"
    if max_size is not None and max_size == 0:
        return BREACHES, "no size fits the hard limits"
    soft_breach = [r for r in rows if r.status == BREACHED]
    if soft_breach:
        return WATCH, f"soft limit {soft_breach[0].limit['limit_id']} has negative headroom"
    if max_size is not None and max_size < CONTEXT.multiply(nav, WATCH_SHARE_OF_NAV):
        return WATCH, "the largest size that fits is under 1% of NAV"
    missing = [r for r in rows if r.status == NOT_COMPUTED]
    if missing:
        return WATCH, f"limit {missing[0].limit['limit_id']} could not be computed"
    return FITS, "every touched limit has headroom"


def fit(portfolio: Portfolio, instrument: Instrument, run: Run) -> Fit:
    held = exposure(portfolio, run.issuer_id)
    pct = CONTEXT.divide(held * HUNDRED, portfolio.nav)
    found = (headroom_row(limit, instrument, portfolio, run) for limit in portfolio.limits)
    rows = tuple(r for r in found if r is not None)
    size, binding = _max_size(rows)
    scale = _scale(portfolio, run)
    if scale is not None:  # amounts in the run's currency and unit
        held, nav = CONTEXT.multiply(held, scale), CONTEXT.multiply(portfolio.nav, scale)
        where = (run.currency, run.unit)
    else:  # every touched limit is Not computed, so no size: amounts stay the portfolio's
        nav, where = portfolio.nav, (portfolio.currency, portfolio.unit)
    outcome, reason = verdict(rows, size, nav)
    return Fit(portfolio, instrument, held, pct, rows, size, binding, outcome, reason, *where)
