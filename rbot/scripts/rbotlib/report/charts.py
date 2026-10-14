"""The chart registry: the ten v1 chart ids, each mapped to the builder of its RBOTCharts spec.

Plan 07 Task 07.4 supplies the builders. Until a builder exists its entry raises
`NotImplementedError` when the chart is rendered, never when the catalog is checked.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

ChartBuilder = Callable[[dict[str, Any]], dict[str, Any]]

CHART_IDS = (
    "chart.model_strip",
    "chart.maturity_wall",
    "chart.capital_structure",
    "chart.ebitda_bridge",
    "chart.adjusted_debt_bridge",
    "chart.rv_loan",
    "chart.rv_hy",
    "chart.talk_range",
    "chart.fit_bullets",
    "chart.issue_counts",
)


def _unbuilt(chart_id: str) -> ChartBuilder:
    def build(_view: dict[str, Any]) -> dict[str, Any]:
        raise NotImplementedError(f"{chart_id}: no builder yet")

    return build


REGISTRY: dict[str, ChartBuilder] = {chart_id: _unbuilt(chart_id) for chart_id in CHART_IDS}
