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
    CodeBlock,
    CoverPage,
    Dashboard,
    KPITile,
    LinkGrid,
    Pipeline,
    ROISummary,
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
    if isinstance(c, Pipeline):
        return _pipeline(c)
    if isinstance(c, LinkGrid):
        return _link_grid(c)
    if isinstance(c, CodeBlock):
        return _code_block(c)
    if isinstance(c, CoverPage):
        return _cover_page(c)
    if isinstance(c, ROISummary):
        return _roi_summary(c)
    return f"<!-- unknown component: {type(c).__name__} -->"


def _cover_page(c: CoverPage) -> str:
    """Markdown: # title + _subtitle_ + key-value lines."""
    lines: List[str] = []
    if c.logo_initials:
        lines.append(f"```")
        lines.append(f" [{c.logo_initials}] ")
        lines.append(f"```")
    lines.append(f"# {c.title}")
    if c.subtitle:
        lines.append(f"_{c.subtitle}_")
    lines.append("")
    if c.prepared_for:
        lines.append(f"**Prepared for:** {c.prepared_for}  ")
    if c.prepared_by:
        lines.append(f"**Prepared by:** {c.prepared_by}  ")
    if c.version:
        lines.append(f"**Version:** {c.version}")
    lines.append("---")
    return "\n".join(lines)


def _roi_summary(c: ROISummary) -> str:
    """Markdown: bullet list with multiplier emphasized."""
    return (
        f"### **{c.multiplier} ROI**\n"
        f"- **Investment:** ${c.investment_usd:,.0f}\n"
        f"- **Monthly recovery:** ${c.monthly_recovery_usd:,.0f}\n"
        f"- **Annual recovery:** ${c.annual_recovery_usd:,.0f}\n"
        f"- **Payback:** {c.payback_months:.1f} months"
    )


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


_STATE_GLYPH = {
    "ready": "[+]",
    "watching": "[~]",
    "blocked": "[!]",
    "shipped": "[=]",
    "neutral": "[ ]",
}


def _pipeline(c: Pipeline) -> str:
    out: List[str] = []
    if c.caption:
        out.append(f"**{c.caption}**")
        out.append("")
    for i, st in enumerate(c.stages, start=1):
        glyph = _STATE_GLYPH.get(st.state, "[ ]")
        line = f"{i:02d}. {glyph} **{st.name}** = `{st.value}`"
        if st.detail:
            line += f" - {st.detail}"
        out.append(line)
    return "\n".join(out)


def _link_grid(c: LinkGrid) -> str:
    out: List[str] = []
    if c.caption:
        out.append(f"**{c.caption}**")
        out.append("")
    for it in c.items:
        kicker = f"_{it.kicker}_ - " if it.kicker else ""
        flag = ""
        if it.ok is True:
            flag = " [OK]"
        elif it.ok is False:
            flag = " [MISSING]"
        suffix = f" - {it.detail}" if it.detail else ""
        out.append(f"- {kicker}[{it.label}]({it.href}){flag}{suffix}")
    return "\n".join(out)


def _code_block(c: CodeBlock) -> str:
    lang = c.language or ""
    cap = f"**{c.caption}**\n\n" if c.caption else ""
    return f"{cap}```{lang}\n{c.text}\n```"


__all__ = ["render_markdown"]
