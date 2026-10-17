#!/usr/bin/env python3
"""Build the design-fixture runs (FIXTURES.md §2) into design/claude-design-handoff/data/test/.

    python3 build-fixtures.py                      build every run whose content modules all exist
    python3 build-fixtures.py --only <run name>    build one run
    python3 build-fixtures.py --check              also run every FIXTURES §6 check; exit 1 on any failure

A run whose content modules are not all present is not written: it is reported as
"incomplete: missing CP-…" and the build exits 1. There are no placeholder handoffs.
"""

from __future__ import annotations

import argparse
import importlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import lib  # noqa: E402
from core import OUT_DIR, slug  # noqa: E402

CZR = {"name": "Caesars Entertainment, Inc.", "id": "CZR", "ticker": "CZR"}
LLG = {"name": "Larchmere Leisure Group, Inc. (fictional)", "id": "LLG-FICTIONAL", "ticker": ""}
CZR_FIT_EXCLUDE = ("cei_rcf", "cei_term_a", "cva_rcf", "cva_term", "sid_bonds", "other_debt")
CZR_CP4C_NA = {
    "chart.value_allocation": "CZR's real distress gate is Not met, so there is no waterfall to draw (the Larchmere run shows it)",
    "chart.recovery_by_class": "CZR's real distress gate is Not met, so there are no recoveries to draw (the Larchmere run shows it)",
}


def _run(
    rid: str, pathway: str, depth: str, variant: str, issuer: dict = CZR, **kw: object
) -> dict:
    return {
        "run_id": rid,
        "pathway": pathway,
        "depth": depth,
        "variant": variant,
        "issuer": issuer,
        "pkg": "larchmere" if issuer is LLG else "czr",
        **kw,
    }


RUNS: dict[str, dict] = {
    "czr-full-credit-assessment": _run(
        "FIX-CZR-FCA-001",
        "FULL_CREDIT_ASSESSMENT",
        "full",
        "primary",
        primary=True,
        portfolios=["lib:test_clo_i"],
        fit_exclude=CZR_FIT_EXCLUDE,
        n_a_charts=CZR_CP4C_NA,
        notes=[
            "Primary: the merger financing is three synthetic tranches; PF-LTM, PROJECTION, CP-DR answers and the Test CLO I Fit are synthetic and say so in their citations."
        ],
    ),
    "czr-full-credit-assessment-quick": _run(
        "FIX-CZR-FCAQ-001",
        "FULL_CREDIT_ASSESSMENT",
        "quick",
        "quick",
        primary=True,
        portfolios=["lib:test_clo_i"],
        fit_exclude=CZR_FIT_EXCLUDE,
        notes=["Quick depth: CP-L10 screen; CP-6 basis Screening."],
    ),
    "czr-earnings-update": _run(
        "FIX-CZR-EU-001",
        "EARNINGS_UPDATE",
        "full",
        "earnings",
        prior="czr.prior_case:build",
        notes=["With a synthetic Prior Case dated 2026-08-05."],
    ),
    "czr-relative-value": _run(
        "FIX-CZR-RV-001",
        "RELATIVE_VALUE",
        "full",
        "rv",
        primary=True,
        portfolios=["lib:test_clo_i"],
        fit_exclude=CZR_FIT_EXCLUDE,
        notes=["Synthetic loan marks and spread curve."],
    ),
    "czr-relative-value-blocked": _run(
        "FIX-CZR-RVB-001",
        "RELATIVE_VALUE",
        "full",
        "rv_blocked",
        primary=True,
        portfolios=["lib:test_clo_i"],
        fit_exclude=CZR_FIT_EXCLUDE,
        n_a_charts={
            "chart.spread_curve": "CP-3D is Blocked: no market observations admitted",
            "chart.implied_pd": "CP-3D is Blocked: no market observations admitted",
        },
        notes=["State variant: CP-3D Blocked."],
    ),
    "czr-covenant-refinancing": _run(
        "FIX-CZR-CR-001",
        "COVENANT_REFINANCING",
        "full",
        "covenant",
        primary=True,
        notes=["Real covenant extraction plus synthetic RP and investment basket usage."],
    ),
    "czr-portfolio-decision": _run(
        "FIX-CZR-PD-001",
        "PORTFOLIO_DECISION",
        "full",
        "portfolio",
        primary=True,
        portfolios=["lib:test_clo_i", "czr.portfolios:indexed_hy"],
        fit_exclude=CZR_FIT_EXCLUDE,
        notes=["Two portfolios; one instrument Breaches."],
    ),
    "larchmere-distressed-restructuring": _run(
        "FIX-LLG-DR-001",
        "DISTRESSED_RESTRUCTURING",
        "full",
        "distressed",
        issuer=LLG,
        issuer_fictional=True,
        primary=True,
        deep_research=False,
        skip_reasons={
            "CP-DR": "not run: no research questions approved",
            "CP-8": "not run: no Prior Case",
        },
        n_a_charts={"chart.rating_triggers": "CP-2H is Blocked: no rating-agency report admitted"},
        portfolios=["larchmere.portfolios:synthetic_clo"],
        fit_exclude=(),
        notes=[
            "Fully fictional issuer: Gate Met, a covenant Breached and one Tight, fulcrum migrates by scenario."
        ],
    ),
}


def _load(spec: str):
    mod, _, attr = spec.partition(":")
    return getattr(importlib.import_module(mod), attr)


def build_run(ctx: lib.Ctx, name: str, cfg: dict) -> tuple[dict | None, str | None]:
    """(run json, None) or (None, reason it is incomplete)."""
    pkg = cfg["pkg"]
    missing_extra: list[str] = []
    portfolios = []
    for p in cfg.get("portfolios", []):
        try:
            fn = _load(p)
        except (ImportError, AttributeError):
            missing_extra.append(f"portfolio {p}")
            continue
        portfolios.append(fn(ctx))
    prior = None
    if cfg.get("prior"):
        try:
            prior = _load(cfg["prior"])(ctx)
        except (ImportError, AttributeError):
            missing_extra.append(f"prior case {cfg['prior']}")
    builders = {}
    plan = ctx.spec["pathways"][cfg["pathway"]]["depths"][cfg["depth"]]
    for step in plan:
        if step in ("MODEL", "PROJECTION", "FIT"):
            continue
        try:
            builders[step] = importlib.import_module(f"{pkg}.{slug(step)}").build
        except ModuleNotFoundError as exc:
            if exc.name != f"{pkg}.{slug(step)}":
                raise
    try:
        rb_mod = importlib.import_module(f"{pkg}.run_brief")
    except ModuleNotFoundError:
        return None, "incomplete: missing RUN_BRIEF"
    run = lib.Run(
        ctx,
        name,
        cfg["run_id"],
        cfg["pathway"],
        cfg["depth"],
        cfg["issuer"],
        primary=cfg.get("primary", False),
        variant=cfg["variant"],
        issuer_fictional=cfg.get("issuer_fictional", False),
        notes=list(cfg.get("notes", [])),
        portfolios=portfolios,
        fit_exclude=tuple(cfg.get("fit_exclude", ())),
        deep_research=cfg.get("deep_research", True),
        prior_case=prior,
        n_a_charts=dict(cfg.get("n_a_charts", {})),
        skip_reasons=dict(cfg.get("skip_reasons", {})),
    )
    try:
        run.build(
            builders,
            lambda c, rid, var: rb_mod.build(
                c, rid, var, pathway=cfg["pathway"], depth=cfg["depth"]
            ),
        )
    except lib.IncompleteRun as exc:
        return None, str(exc) + (", " + ", ".join(missing_extra) if missing_extra else "")
    if missing_extra:
        return None, "incomplete: missing " + ", ".join(missing_extra)
    return run.to_json(), None


def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument("--only", action="append", help="build only this run name (repeatable)")
    ap.add_argument(
        "--check", action="store_true", help="run every FIXTURES §6 check on each built run"
    )
    args = ap.parse_args()
    names = args.only or list(RUNS)
    unknown = [n for n in names if n not in RUNS]
    if unknown:
        print(f"unknown run(s): {', '.join(unknown)}; known: {', '.join(RUNS)}")
        return 2
    ctx = lib.load_ctx()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    bad = 0
    for name in names:
        data, why = build_run(ctx, name, RUNS[name])
        if data is None:
            print(f"{name}: {why}")
            bad += 1
            continue
        path = OUT_DIR / f"{name}.run.json"
        path.write_text(json.dumps(data, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"{name}: written ({path.stat().st_size // 1024} KB)")
        if args.check:
            fails = lib.check(data, ctx)
            for f in fails:
                print(f"  FAIL {f}")
            if fails:
                bad += 1
            else:
                print("  checks pass")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
