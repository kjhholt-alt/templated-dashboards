"""Markdown renderer.

Plain CommonMark-friendly output. Designed for terminal preview and
Discord blocks. ``chart`` components degrade to a callout-like note.
"""

from __future__ import annotations

from typing import List

from ..components import callout as callout_helpers
from ..components import kpi_tile as kpi_helpers
from ..components import status_card as status_helpers
from ..components import table as table_helpers
from ..ir import (
    Callout,
    Chart,
    Dashboard,
    KPITile,
    Section,
    StatusCard,
    Table,
    Timeline,
)

_TIER_GLYPH = {"good": "[+]", "warn": "[~]", "bad": "[x]", "neutral": "[ ]"}


def render_markdown(dash: Dashboard) -> str:
    parts: List[str] = []
    parts.append(f"# {dash.title}")
    if dash.subtitle:
        parts.append(f"_{dash.subtitle}_")
    parts.append("")
    for s in dash.sections:
        parts.append(_section(s))
    if dash.footer:
        parts.append("")
        parts.append(f"---")
        parts.append(dash.footer)
    return "\n".join(parts).rstrip() + "\n"


def _section(s: Section) -> str:
    out: List[str] = [f"## {s.title}"]
    if s.subtitle:
        out.append(f"_{s.subtitle}_")
    out.append("")
    for c in s.components:
        out.append(_component(c))
        out.append("")
    return "\n".join(out)


def _component(c) -> str:
    if isinstance(c, StatusCard):
        return _status(c)
    if isinstance(c, KPITile):
        return _kpi(c)
    if isinstance(c, Table):
        return _table(c)
    if isinstance(c, Timeline):
        return _timeline(c)
    if isinstance(c, Callout):
        return _callout(c)
    if isinstance(c, Chart):
        return _chart_fallback(c)
    return f"<!-- unknown component: {type(c).__name__} -->"


def _status(c: StatusCard) -> str:
    r = status_helpers.resolve(c)
    glyph = _TIER_GLYPH.get(r["tier"], "[ ]")
    line = f"- {glyph} **{r['project'] or c.project}**"
    if r["summary"]:
        line += f" - {r['summary']}"
    if r["last_update"]:
        line += f"  _(updated {r['last_update']})_"
    return line


def _kpi(c: KPITile) -> str:
    delta = f" ({c.delta})" if c.delta else ""
    return f"- **{c.label}**: `{kpi_helpers.format_value(c)}`{delta}"


def _table(c: Table) -> str:
    rows = table_helpers.normalise_rows(c)
    out: List[str] = []
    if c.caption:
        out.append(f"**{c.caption}**")
        out.append("")
    out.append("| " + " | ".join(_md_cell(h) for h in c.headers) + " |")
    out.append("| " + " | ".join("---" for _ in c.headers) + " |")
    for row in rows:
        out.append("| " + " | ".join(_md_cell(cell) for cell in row) + " |")
    return "\n".join(out)


def _md_cell(s: str) -> str:
    return s.replace("|", "\\|").replace("\n", " ")


def _timeline(c: Timeline) -> str:
    out: List[str] = []
    for ev in c.events:
        glyph = _TIER_GLYPH.get(ev.tone, "[ ]")
        line = f"- {glyph} **{ev.when}** - {ev.title}"
        if ev.detail:
            line += f"  \n  {ev.detail}"
        out.append(line)
    return "\n".join(out)


def _callout(c: Callout) -> str:
    icon = callout_helpers.icon_for(c)
    return f"> **[{icon}]** {c.text}"


def _chart_fallback(c: Chart) -> str:
    series = ", ".join(s.label for s in c.series)
    cap = f" - {c.caption}" if c.caption else ""
    return f"> **[chart:{c.kind}]** {series}{cap} _(chart omitted in markdown)_"


__all__ = ["render_markdown"]
