"""HTML renderer.

Self-contained: emits a single HTML file with inlined theme CSS and a
small Tailwind-CDN reset for utility classes (no build step). All user
content is escaped via ``html.escape``.
"""

from __future__ import annotations

import html
from typing import List

from ..components import callout as callout_helpers
from ..components import chart as chart_helpers
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
from ..themes import get as theme_css

_TAILWIND_CDN = (
    '<script src="https://cdn.tailwindcss.com?plugins=forms,typography"></script>'
)


def render_html(dash: Dashboard, *, include_tailwind: bool = True) -> str:
    """Return a complete, standalone HTML document for the dashboard."""
    css = theme_css(dash.theme)
    body = _render_body(dash)
    head_extras = _TAILWIND_CDN if include_tailwind else ""
    return _PAGE.format(
        title=html.escape(dash.title),
        css=css,
        head_extras=head_extras,
        body=body,
    )


_PAGE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>{title}</title>
{head_extras}
<style>{css}</style>
</head>
<body>
<main class="dash">
{body}
</main>
</body>
</html>
"""


def _render_body(dash: Dashboard) -> str:
    parts: List[str] = []
    parts.append('<header class="dash-head">')
    parts.append(f'<div class="dash-title">{html.escape(dash.title)}</div>')
    if dash.subtitle:
        parts.append(
            f'<div class="dash-subtitle">{html.escape(dash.subtitle)}</div>'
        )
    parts.append("</header>")

    for section in dash.sections:
        parts.append(_render_section(section))

    if dash.footer:
        parts.append(
            f'<footer class="dash-footer">{html.escape(dash.footer)}</footer>'
        )
    return "\n".join(parts)


def _render_section(section: Section) -> str:
    parts: List[str] = ['<section class="section">']
    parts.append('<div class="section-head">')
    parts.append(
        f'<div class="section-title">{html.escape(section.title)}</div>'
    )
    if section.subtitle:
        parts.append(
            f'<div class="section-subtitle">{html.escape(section.subtitle)}</div>'
        )
    parts.append("</div>")

    layout_class = "section-grid" if section.layout == "grid" else "section-stack"
    parts.append(f'<div class="{layout_class}">')
    for c in section.components:
        parts.append(_render_component(c))
    parts.append("</div>")
    parts.append("</section>")
    return "\n".join(parts)


def _render_component(c) -> str:
    if isinstance(c, StatusCard):
        return _status_card(c)
    if isinstance(c, KPITile):
        return _kpi(c)
    if isinstance(c, Table):
        return _table(c)
    if isinstance(c, Timeline):
        return _timeline(c)
    if isinstance(c, Callout):
        return _callout(c)
    if isinstance(c, Chart):
        return _chart(c)
    return f"<!-- unknown component: {type(c).__name__} -->"


def _status_card(c: StatusCard) -> str:
    resolved = status_helpers.resolve(c)
    tier = resolved["tier"]
    project = html.escape(resolved["project"] or c.project)
    summary = html.escape(resolved["summary"] or "")
    last = html.escape(resolved["last_update"] or "")
    return (
        f'<div class="status-card tone-{tier}">'
        f'<span class="status-dot"></span>'
        f'<div class="status-body">'
        f'<div class="status-project">{project}</div>'
        f'<div class="status-summary">{summary}</div>'
        f"</div>"
        f'<div class="status-meta">{last}</div>'
        f"</div>"
    )


def _kpi(c: KPITile) -> str:
    delta_html = ""
    if c.delta:
        delta_html = f'<div class="kpi-delta">{html.escape(c.delta)}</div>'
    return (
        f'<div class="kpi tone-{c.tone}">'
        f'<div class="kpi-label">{html.escape(c.label)}</div>'
        f'<div class="kpi-value">{html.escape(kpi_helpers.format_value(c))}</div>'
        f"{delta_html}"
        f"</div>"
    )


def _table(c: Table) -> str:
    rows = table_helpers.normalise_rows(c)
    head = "".join(f"<th>{html.escape(h)}</th>" for h in c.headers)
    body_rows = []
    for row in rows:
        cells = "".join(f"<td>{html.escape(cell)}</td>" for cell in row)
        body_rows.append(f"<tr>{cells}</tr>")
    cap = ""
    if c.caption:
        cap = f'<div class="tbl-caption">{html.escape(c.caption)}</div>'
    return (
        '<div class="tbl-wrap">'
        f"{cap}"
        '<table class="tbl">'
        f"<thead><tr>{head}</tr></thead>"
        f'<tbody>{"".join(body_rows)}</tbody>'
        "</table>"
        "</div>"
    )


def _timeline(c: Timeline) -> str:
    events = []
    for ev in c.events:
        detail = ""
        if ev.detail:
            detail = f'<div class="tl-detail">{html.escape(ev.detail)}</div>'
        events.append(
            f'<div class="tl-event tone-{ev.tone}">'
            f'<span class="tl-marker"></span>'
            f'<div class="tl-body">'
            f'<div class="tl-when">{html.escape(ev.when)}</div>'
            f'<div class="tl-title">{html.escape(ev.title)}</div>'
            f"{detail}"
            f"</div>"
            f"</div>"
        )
    return f'<div class="timeline">{"".join(events)}</div>'


def _callout(c: Callout) -> str:
    icon = html.escape(callout_helpers.icon_for(c))
    return (
        f'<div class="callout tone-{c.tone}">'
        f'<div class="callout-icon">{icon}</div>'
        f'<div class="callout-text">{html.escape(c.text)}</div>'
        f"</div>"
    )


def _chart(c: Chart) -> str:
    cap = ""
    if c.caption:
        cap = f'<div class="chart-caption">{html.escape(c.caption)}</div>'
    svg = _svg_for_chart(c)
    return f'<div class="chart">{cap}{svg}</div>'


def _svg_for_chart(c: Chart) -> str:
    """Tiny inline SVG rendering. No external deps."""
    width = 600
    height = 140
    pad = 8
    lo, hi = chart_helpers.y_range(c)
    span = (hi - lo) or 1.0
    if not c.series:
        return ""
    max_n = max(len(s.points) for s in c.series) or 1
    parts = [
        f'<svg viewBox="0 0 {width} {height}" preserveAspectRatio="none" '
        'xmlns="http://www.w3.org/2000/svg" role="img">'
    ]
    palette = ["#38bdf8", "#fbbf24", "#22c55e", "#ef4444", "#a855f7"]

    if c.kind == "bar":
        bar_w = max(1.0, (width - 2 * pad) / max(max_n, 1) - 2)
        for i, series in enumerate(c.series):
            colour = palette[i % len(palette)]
            for j, p in enumerate(series.points):
                x = pad + j * ((width - 2 * pad) / max_n)
                y = height - pad - ((p - lo) / span) * (height - 2 * pad)
                h_bar = (height - pad) - y
                parts.append(
                    f'<rect x="{x:.2f}" y="{y:.2f}" width="{bar_w:.2f}" '
                    f'height="{h_bar:.2f}" fill="{colour}" opacity="0.85" />'
                )
    else:  # line / sparkline
        for i, series in enumerate(c.series):
            colour = palette[i % len(palette)]
            pts = []
            n = len(series.points) or 1
            for j, p in enumerate(series.points):
                x = pad + j * ((width - 2 * pad) / max(n - 1, 1))
                y = height - pad - ((p - lo) / span) * (height - 2 * pad)
                pts.append(f"{x:.2f},{y:.2f}")
            parts.append(
                f'<polyline fill="none" stroke="{colour}" stroke-width="2" '
                f'points="{" ".join(pts)}" />'
            )

    parts.append("</svg>")
    return "".join(parts)


__all__ = ["render_html"]
