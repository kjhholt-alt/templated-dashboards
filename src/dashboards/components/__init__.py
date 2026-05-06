"""Component models live alongside the IR for cohesion.

This package re-exports them so ``from dashboards.components import KPITile``
also works. The canonical home is ``dashboards.ir``.
"""

from ..ir import (
    StatusCard,
    KPITile,
    Table,
    Timeline,
    TimelineEvent,
    Callout,
    Chart,
    ChartSeries,
    Pipeline,
    PipelineStage,
    LinkGrid,
    LinkItem,
    CodeBlock,
)

# Per-component shorthand modules (placeholders for future per-component logic).
from . import status_card, kpi_tile, table, timeline, callout, chart  # noqa: F401

__all__ = [
    "StatusCard",
    "KPITile",
    "Table",
    "Timeline",
    "TimelineEvent",
    "Callout",
    "Chart",
    "ChartSeries",
    "Pipeline",
    "PipelineStage",
    "LinkGrid",
    "LinkItem",
    "CodeBlock",
]
