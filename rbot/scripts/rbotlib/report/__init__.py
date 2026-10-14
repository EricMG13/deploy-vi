"""The Report renderer: a finished run to `report.html` and `report.md` (Plan 07)."""

from __future__ import annotations


class ReportError(ValueError):
    """Every refusal of the Report renderer; `render` prints it and exits 1."""
