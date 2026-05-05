"""templated-dashboards: data -> IR -> HTML/Markdown/Excel/PDF."""

from .ir import (
    Dashboard as DashboardIR,
    Section,
    Component,
    StatusCard,
    KPITile,
    Table,
    Timeline,
    TimelineEvent,
    Callout,
    Chart,
    ChartSeries,
    Tone,
    load,
    dump,
)
from .builder import Dashboard
from .render import render, UnsupportedComponent, UnsupportedRenderer

__version__ = "0.1.0"

__all__ = [
    "Dashboard",
    "DashboardIR",
    "Section",
    "Component",
    "StatusCard",
    "KPITile",
    "Table",
    "Timeline",
    "TimelineEvent",
    "Callout",
    "Chart",
    "ChartSeries",
    "Tone",
    "load",
    "dump",
    "render",
    "UnsupportedComponent",
    "UnsupportedRenderer",
    "__version__",
]
