"""Public API of the fixture generator. Content modules import everything from here.

from lib import Handoff, load_ctx, compute, plain, fx, fpct, ModelBuilder, fit, Run, check
"""

from checks import check
from core import (
    GAP,
    Ctx,
    D,
    FixtureError,
    Handoff,
    check_calc_string,
    compute,
    fbps,
    fpct,
    fx,
    load_ctx,
    plain,
    q,
    ratio,
    slug,
)
from fit import FitResult, cp6_rows, fit, fit_handoff, rating_bucket, test_clo_i, weaker
from fit_inputs import fit_instruments
from helpers import caos_text, cell_number, cite_row, doc_row, join_marks
from model import ModelBuilder, ModelInputError, model_handoff, projection_handoff
from run import IncompleteRun, Run, diff_tables

__all__ = [
    "GAP",
    "D",
    "Ctx",
    "FixtureError",
    "FitResult",
    "Handoff",
    "IncompleteRun",
    "ModelBuilder",
    "ModelInputError",
    "Run",
    "caos_text",
    "cell_number",
    "check",
    "check_calc_string",
    "cite_row",
    "compute",
    "cp6_rows",
    "diff_tables",
    "doc_row",
    "fbps",
    "fit",
    "fit_handoff",
    "fit_instruments",
    "fpct",
    "fx",
    "join_marks",
    "load_ctx",
    "model_handoff",
    "plain",
    "projection_handoff",
    "q",
    "ratio",
    "rating_bucket",
    "slug",
    "test_clo_i",
    "weaker",
]
