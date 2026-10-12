"""Portfolio Fit arithmetic (interfaces spec section 7), pure Decimal with no I/O.

For one portfolio (`prepared/portfolios/<id>.json`) and one instrument:

1. `current_exposure` = the par of the portfolio's positions in the run's issuer (a position
   belongs to it when its `issuer_id` equals the run's, or its `issuer_name` equals the run's
   issuer name, both casefolded); `current_exposure_pct_nav` = that / NAV x 100. A position
   matched by name only is counted and the fit is a Watch (the ids disagree).
2. The limits the instrument touches: every `issuer` limit, whose current value is the run
   issuer's own exposure in the limit's unit (the file's figure is its largest obligor); a
   `sector`, `country`, `rating_bucket`, `asset_type`, `seniority`, `maturity` or `currency`
   limit when its `scope_value` (a list written with commas, or one name that holds commas)
   names the instrument's attribute, or when it is a "largest bucket" limit (`largest`), whose
   current value bounds every bucket. A sector or country that is in neither the listed values
   nor the portfolio's own taxonomy (its positions' and limits' values) is `Not computed`, never
   "does not touch"; so is a limit without a `scope_value` that is not a largest-bucket limit.
   An instrument with no rating, or one RBOT cannot read, counts toward the CCC bucket limit
   (and is flagged in `notes`). Headroom is the limit less the current value in the limit's unit
   (for a maturity limit in years, the limit less the instrument's tenor); `headroom_amount`
   converts it to the run's currency and unit (`pct_nav` x NAV / 100, `pct_par` x par / 100,
   `amount` as is); a count limit with headroom under 1, or a maturity limit with none left,
   caps the size at 0, otherwise it caps none (`headroom_amount` None). A touched limit is
   `Not computed` when the instrument's attribute it needs is missing, the NAV or par it needs
   is not positive, or the portfolio's currency or unit is not the run's. An `other` limit (a
   book statistic such as top-10 concentration or WAL) is shown `From file` and never binds.
3. `max_size` = the smallest `headroom_amount` over the computed Hard limits, floored at 0;
   `binding_limit` is the limit giving it (none when no Hard limit caps the size). A Hard limit
   that is `Not computed` leaves `max_size` an upper bound (`Fit.uncomputed_hard`).
4. `verdict`: `Breaches` when a Hard limit has negative headroom or `max_size` is 0; `Watch`
   when a Soft limit has negative headroom, `max_size` is under 1% of NAV, a touched limit is
   `Not computed`, a Hard book statistic is already breached in the file, a position or limit
   row of the portfolio could not be read (`unparsed`), or an exposure matched by name only;
   otherwise `Fits`.
5. `recommendation_cap`: `Breaches` -> `Avoid`, `Watch` -> `3 - MW`, `Fits` -> `1 - Strong OW`
   (no cap).

Rows `rbot prepare` could not read are in the portfolio's `unparsed` list, each with a `kind`:
`position` and `limit` (a Hard or Soft row whose figure could not be read) lower the verdict
to Watch; `minimum` (a floor Portfolio Fit does not size against), `info` and `meta` go to the
FIT Handoff's `## Gaps` only.
"""

from __future__ import annotations

import re
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, replace
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
TAXONOMY = ("sector", "country")  # free text from the filings: matched against the portfolio's own
WATCH_KINDS = ("position", "limit")  # unparsed rows that lower the verdict
# A unit a portfolio's amounts may be written in. Blank is not here: it cannot be scaled.
_SCALE = {
    "units": Decimal(1),
    "usd": Decimal(1),
    "eur": Decimal(1),
    "gbp": Decimal(1),
    "thousands": Decimal(1000),
    "millions": Decimal(1_000_000),
}
_LOANS = frozenset({"RCF", "1L Term Loan", "2L Term Loan", "DIP Financing"})
_BONDS = frozenset({"SS Notes", "SU Notes", "Sub Debt", "PIK", "Hybrid"})
_SENIOR = frozenset({"RCF", "1L Term Loan", "SS Notes", "DIP Financing"})
_JUNIOR_WORDS = ("unsecured", "2nd lien", "second lien", "subordinated", "junior")
_SENIOR_WORDS = ("1st lien", "first lien", "senior secured")
_BOND_WORDS = ("bond", "note")
_LOAN_WORDS = ("loan",)
_MOODYS_ORDER = (
    "Aaa Aa1 Aa2 Aa3 A1 A2 A3 Baa1 Baa2 Baa3 Ba1 Ba2 Ba3 B1 B2 B3 Caa1 Caa2 Caa3 Ca C"
).split()
_SP_ORDER = "AAA AA+ AA AA- A+ A A- BBB+ BBB BBB- BB+ BB BB- B+ B B- CCC+ CCC CCC- CC C D".split()
_MOODYS = {r.casefold(): n for n, r in enumerate(_MOODYS_ORDER)}
_SP = {r.casefold(): n for n, r in enumerate(_SP_ORDER)}
_MOODYS_EDGES = (("baa3", "IG"), ("ba3", "BB"), ("b3", "B"))
_SP_EDGES = (("bbb-", "IG"), ("bb-", "BB"), ("b-", "B"))
_NOT_RATED = frozenset({"", "nr", "n/r", "wr", "wd", "na", "n/a", "unrated", "-", "\N{EM DASH}"})
BUCKETS = ("IG", "BB", "B", "CCC")
UNRATED, UNREADABLE = "Unrated", "Unreadable"
_COMPANY_WORDS = frozenset(
    "inc incorporated corp corporation co company ltd limited llc lp plc sa nv ag the".split()
)


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
    nav: Decimal | None  # None: missing or not a positive figure
    par: Decimal | None
    currency: str
    unit: str
    positions: tuple[Mapping[str, Any], ...]
    limits: tuple[Mapping[str, Any], ...]
    unparsed: tuple[Mapping[str, str], ...] = ()


@dataclass(frozen=True, slots=True)
class Run:
    issuer_id: str
    as_of: date
    currency: str
    unit: str
    issuer_names: tuple[str, ...] = ()  # the issuer's name and aliases, as the Run Brief has them


@dataclass(frozen=True, slots=True)
class Headroom:
    limit: Mapping[str, Any]
    current_value: Decimal | None
    headroom: Decimal | None
    headroom_amount: Decimal | None  # in the run's unit; None: does not cap the size
    status: str


@dataclass(frozen=True, slots=True)
class Held:
    """The run issuer's positions in one portfolio."""

    par: Decimal
    count: int
    sector: str | None  # the portfolio's own words for the issuer, when its positions agree
    country: str | None
    by_name_only: tuple[str, ...]  # `issuer_id` of positions matched by issuer name alone


@dataclass(frozen=True, slots=True)
class Fit:
    portfolio: Portfolio
    instrument: Instrument
    current_exposure: Decimal
    current_exposure_pct_nav: Decimal | None  # None: the NAV is not a positive figure
    rows: tuple[Headroom, ...]
    max_size: Decimal | None  # None: no Hard limit caps the size
    binding_limit: str | None
    verdict: str
    reason: str
    currency: str  # of current_exposure and max_size: the run's, else the portfolio's
    unit: str
    notes: tuple[str, ...] = ()  # what the Gaps section of the FIT Handoff says about this fit
    positions_held: int = 0  # positions counted as the run issuer's

    @property
    def recommendation_cap(self) -> str:
        return CAP[self.verdict]

    @property
    def uncomputed_hard(self) -> tuple[str, ...]:
        """Hard limits that could not be computed: `max_size` ignores them."""
        return tuple(
            str(r.limit["limit_id"])
            for r in self.rows
            if r.status == NOT_COMPUTED and r.limit["limit_kind"] == "Hard"
        )


# --- instrument attributes -------------------------------------------------------------------


def rating_bucket(ratings: Sequence[str]) -> str:
    """The lowest bucket over the agencies' ratings (IG, BB, B, CCC).

    `Unrated` when there is no rating (or only NR / WR); `Unreadable` when RBOT can read none.
    """
    written = [r for r in ratings if r.strip().casefold() not in _NOT_RATED]
    if not written:
        return UNRATED
    found = [b for b in (_bucket(r) for r in written) if b is not None]
    if not found:
        return UNREADABLE
    return max(found, key=BUCKETS.index)


def _bucket(rating: str) -> str | None:
    """A rating's bucket, after dropping `(P)`, `(sf)`, `*-` watch marks and Moody's `u`."""
    text = re.sub(r"\([^)]*\)", "", rating)
    text = re.sub(r"\*[+-]?", "", text).strip().casefold()
    text = text[:-1] if re.fullmatch(r"[a-z]+\d?u", text) else text
    if text in _MOODYS:
        rank = _MOODYS[text]
        return next((b for edge, b in _MOODYS_EDGES if rank <= _MOODYS[edge]), "CCC")
    if text in _SP:
        rank = _SP[text]
        return next((b for edge, b in _SP_EDGES if rank <= _SP[edge]), "CCC")
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


def _fold(text: object) -> str:
    return " ".join(str(text).casefold().split())


def scope_values(limit: Mapping[str, Any]) -> list[str]:
    """The names a limit lists, casefolded: its `scope_values`, else `scope_value` as one name
    and, split on commas, as a list (a sector name may hold a comma)."""
    listed = limit.get("scope_values")
    if listed:
        return [_fold(v) for v in listed]
    raw = limit.get("scope_value")
    if raw is None:
        return []
    whole = _fold(raw)
    return [whole, *(w for w in (_fold(p) for p in str(raw).split(",")) if w and w != whole)]


def vocabulary(portfolio: Portfolio) -> dict[str, frozenset[str]]:
    """Per taxonomy scope, the names the portfolio itself uses: its positions' and its limits'."""
    found: dict[str, set[str]] = {scope: set() for scope in TAXONOMY}
    for position in portfolio.positions:
        for scope in TAXONOMY:
            if position.get(scope):
                found[scope].add(_fold(position[scope]))
    for limit in portfolio.limits:
        if limit["scope"] in found:
            found[limit["scope"]].update(scope_values(limit))
    return {scope: frozenset(names) for scope, names in found.items()}


def _seniority_match(scope_value: str, instrument: Instrument) -> bool | None:
    senior = is_senior_secured(instrument)
    text = scope_value.casefold()
    kind = asset_type(instrument.debt_type)
    if kind == "Loan" and any(w in text for w in _BOND_WORDS):
        return False
    if kind == "Bond" and any(w in text for w in _LOAN_WORDS):
        return False
    if any(w in text for w in _JUNIOR_WORDS):
        return None if senior is None else not senior
    if any(w in text for w in _SENIOR_WORDS):
        return senior
    return False


def _rating_touch(values: list[str], bucket: str) -> bool:
    """A rating bucket limit; unrated and unreadable count toward the CCC bucket."""
    if bucket.casefold() in values:
        return True
    unrated = bucket in (UNRATED, UNREADABLE)
    return unrated and any(v in values for v in ("ccc", UNRATED.casefold()))


def counted_as_ccc(limit: Mapping[str, Any], instrument: Instrument) -> bool:
    """Whether an unrated or unreadable instrument is counted toward a CCC bucket limit."""
    bucket = rating_bucket(instrument.ratings)
    values = scope_values(limit)
    return (
        limit["scope"] == "rating_bucket"
        and bucket in (UNRATED, UNREADABLE)
        and "ccc" in values
        and bucket.casefold() not in values
    )


def _attribute(scope: str, instrument: Instrument) -> str | None:
    return {
        "sector": instrument.sector,
        "country": instrument.country,
        "currency": instrument.currency,
        "asset_type": asset_type(instrument.debt_type),
        "rating_bucket": rating_bucket(instrument.ratings),
    }[scope]


def touches(
    limit: Mapping[str, Any],
    instrument: Instrument,
    names: Mapping[str, frozenset[str]] | None = None,
) -> bool | None:
    """Whether the limit applies to the instrument; None when that cannot be told.

    `names` is the portfolio's own taxonomy (`vocabulary`). A sector or country outside both
    the limit's list and the taxonomy is unknown (None), not "not touched".
    """
    scope = limit["scope"]
    if scope == "issuer":
        return True
    if scope not in SCOPES:
        return False
    if scope == "maturity":
        return True if instrument.maturity is not None else None
    values = scope_values(limit)
    if not values:
        return True if limit.get("largest") else None
    if scope == "seniority":
        return _seniority_match(str(limit["scope_value"]), instrument)
    attribute = _attribute(scope, instrument)
    if attribute is None:
        return None
    if scope == "rating_bucket":
        return _rating_touch(values, attribute)
    if _fold(attribute) in values:
        return True
    known = (names or {}).get(scope, frozenset()) if scope in TAXONOMY else {_fold(attribute)}
    return False if _fold(attribute) in known else None


def _name(text: object) -> str:
    """An issuer name without punctuation or company-form words: `Caesars Entertainment, Inc.`
    and `CAESARS ENTERTAINMENT INC` agree."""
    words = re.sub(r"[^0-9a-z]+", " ", str(text).casefold()).split()
    return " ".join(w for w in words if w not in _COMPANY_WORDS)


def exposure(portfolio: Portfolio, run: Run) -> Held:
    """The run issuer's positions: by `issuer_id` (casefolded), else by issuer name."""
    wanted = _fold(run.issuer_id)
    names = {n for n in (_name(x) for x in run.issuer_names) if n}
    mine, by_name = [], []
    for p in portfolio.positions:
        if _fold(p.get("issuer_id", "")) == wanted:
            mine.append(p)
        elif names and _name(p.get("issuer_name", "")) in names:
            mine.append(p)
            by_name.append(str(p.get("issuer_id", "")))
    par = sum((Decimal(str(p["par"])) for p in mine), Decimal(0))
    return Held(par, len(mine), _agreed(mine, "sector"), _agreed(mine, "country"), tuple(by_name))


def _agreed(positions: Sequence[Mapping[str, Any]], key: str) -> str | None:
    values = {str(p[key]) for p in positions if p.get(key)}
    return values.pop() if len(values) == 1 else None


def _issuer_current(
    unit: str, held: Held, nav: Decimal | None, par: Decimal | None
) -> Decimal | None:
    """The run issuer's exposure in the limit's unit (portfolio units for an amount)."""
    if unit == "pct_nav":
        return None if nav is None else CONTEXT.divide(held.par * HUNDRED, nav)
    if unit == "pct_par":
        return None if par is None else CONTEXT.divide(held.par * HUNDRED, par)
    if unit == "amount":
        return held.par
    return Decimal(held.count) if unit == "count" else None


def amount(headroom: Decimal, unit: str, portfolio: Portfolio, scale: Decimal) -> Decimal | None:
    """Headroom in the run's unit.

    A count limit with under 1 left, or a maturity limit with none, caps the size at 0;
    otherwise it caps none (None). None too when the NAV or par the unit needs is unknown.
    """
    if unit == "count":
        return Decimal(0) if headroom < 1 else None
    if unit == "years":
        return Decimal(0) if headroom <= 0 else None
    base = {"pct_nav": portfolio.nav, "pct_par": portfolio.par}.get(unit)
    if unit in ("pct_nav", "pct_par"):
        if base is None:
            return None
        return CONTEXT.multiply(CONTEXT.divide(headroom * base, HUNDRED), scale)
    return CONTEXT.multiply(headroom, scale)


def _scale(portfolio: Portfolio, run: Run) -> Decimal | None:
    """The factor from the portfolio's unit to the run's; None when currencies differ."""
    if portfolio.currency != run.currency:
        return None
    mine, theirs = _SCALE.get(_fold(portfolio.unit)), _SCALE.get(_fold(run.unit))
    if mine is None or theirs is None:
        return None
    return CONTEXT.divide(mine, theirs)


@dataclass(frozen=True, slots=True)
class _Context:
    portfolio: Portfolio
    run: Run
    held: Held
    names: Mapping[str, frozenset[str]]


def headroom_row(limit: Mapping[str, Any], instrument: Instrument, c: _Context) -> Headroom | None:
    """The limit's row for the instrument, or None when it does not touch it."""
    if limit["scope"] == "other":
        stated = Decimal(str(limit["current_value"]))
        room = CONTEXT.subtract(Decimal(str(limit["limit_value"])), stated)
        return Headroom(limit, stated, room, None, FROM_FILE)
    touched = touches(limit, instrument, c.names)
    if touched is False:
        return None
    current = _current(limit, instrument, c)
    scale = _scale(c.portfolio, c.run)
    needed = {"pct_nav": c.portfolio.nav, "pct_par": c.portfolio.par}.get(limit["unit"], 1)
    if touched is None or current is None or scale is None or needed is None:
        return Headroom(limit, current, None, None, NOT_COMPUTED)
    room = CONTEXT.subtract(Decimal(str(limit["limit_value"])), current)
    status = BREACHED if room < 0 else WITHIN
    return Headroom(limit, current, room, amount(room, limit["unit"], c.portfolio, scale), status)


def _current(limit: Mapping[str, Any], instrument: Instrument, c: _Context) -> Decimal | None:
    if limit["scope"] == "issuer":
        return _issuer_current(limit["unit"], c.held, c.portfolio.nav, c.portfolio.par)
    if limit["scope"] == "maturity":
        return tenor_years(instrument, c.run.as_of)
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


def verdict(
    rows: Sequence[Headroom],
    max_size: Decimal | None,
    nav: Decimal | None,
    concerns: Sequence[str] = (),
) -> tuple[str, str]:
    """(verdict, reason) by the section 7 order: Breaches, then Watch, then Fits.

    `concerns` are further reasons for Watch (an unreadable row, an exposure matched by name).
    """
    hard_breach = [r for r in rows if r.status == BREACHED and r.limit["limit_kind"] == "Hard"]
    if hard_breach:
        return BREACHES, f"hard limit {hard_breach[0].limit['limit_id']} has negative headroom"
    if max_size is not None and max_size == 0:
        return BREACHES, "no size fits the hard limits"
    soft_breach = [r for r in rows if r.status == BREACHED]
    if soft_breach:
        return WATCH, f"soft limit {soft_breach[0].limit['limit_id']} has negative headroom"
    if (
        max_size is not None
        and nav is not None
        and max_size < CONTEXT.multiply(nav, WATCH_SHARE_OF_NAV)
    ):
        return WATCH, "the largest size that fits is under 1% of NAV"
    missing = [r for r in rows if r.status == NOT_COMPUTED]
    if missing:
        return WATCH, f"limit {missing[0].limit['limit_id']} could not be computed"
    if concerns:
        return WATCH, concerns[0]
    return FITS, "every touched limit has headroom"


def _positive(value: Decimal | None) -> Decimal | None:
    return value if value is not None and value > 0 else None


def _with_own_words(instrument: Instrument, held: Held) -> Instrument:
    """The portfolio's own sector and country for the run issuer, when it holds the issuer."""
    return replace(
        instrument,
        sector=held.sector or instrument.sector,
        country=held.country or instrument.country,
    )


def concerns(portfolio: Portfolio, held: Held, rows: Sequence[Headroom]) -> list[str]:
    """Reasons for Watch that are not a limit row: unreadable rows, an id mismatch, a breach
    already in the file."""
    found = [
        f"{u['row']} could not be read ({u['reason']})"
        for u in portfolio.unparsed
        if u.get("kind", "limit") in WATCH_KINDS
    ]
    if held.by_name_only:
        ids = ", ".join(held.by_name_only)
        found.append(f"positions {ids} matched the issuer by name only; the ids disagree")
    found += [
        f"hard limit {r.limit['limit_id']} is already breached in the file ({r.headroom})"
        for r in rows
        if r.status == FROM_FILE and r.limit["limit_kind"] == "Hard" and (r.headroom or 0) < 0
    ]
    if portfolio.nav is None or portfolio.par is None:
        found.append("the portfolio's NAV or par is not a positive figure")
    return found


def _notes(instrument: Instrument, rows: Sequence[Headroom]) -> tuple[str, ...]:
    return tuple(
        f"{instrument.facility_id}: no readable rating, counted toward {r.limit['limit_id']}"
        for r in rows
        if counted_as_ccc(r.limit, instrument)
    )


def fit(portfolio: Portfolio, instrument: Instrument, run: Run) -> Fit:
    portfolio = replace(portfolio, nav=_positive(portfolio.nav), par=_positive(portfolio.par))
    held = exposure(portfolio, run)
    instrument = _with_own_words(instrument, held)
    context = _Context(portfolio, run, held, vocabulary(portfolio))
    found = (headroom_row(limit, instrument, context) for limit in portfolio.limits)
    rows = tuple(r for r in found if r is not None)
    size, binding = _max_size(rows)
    pct = None if portfolio.nav is None else CONTEXT.divide(held.par * HUNDRED, portfolio.nav)
    scale = _scale(portfolio, run)
    exposed = held.par
    if scale is not None:  # amounts in the run's currency and unit
        exposed, where = CONTEXT.multiply(exposed, scale), (run.currency, run.unit)
    else:  # every touched limit is Not computed, so no size: amounts stay the portfolio's
        where = (portfolio.currency, portfolio.unit)
    outcome, reason = verdict(
        rows, size, _scaled(portfolio.nav, scale), concerns(portfolio, held, rows)
    )
    return Fit(
        portfolio,
        instrument,
        exposed,
        pct,
        rows,
        size,
        binding,
        outcome,
        reason,
        *where,
        _notes(instrument, rows),
        held.count,
    )


def _scaled(value: Decimal | None, scale: Decimal | None) -> Decimal | None:
    if value is None:
        return None
    return value if scale is None else CONTEXT.multiply(value, scale)
