# templated-dashboards

A small, opinionated templating library that turns structured data
(an *Intermediate Representation*) into HTML, Markdown, Excel, and PDF
dashboards. One IR in, four formats out.

## Why

Two real consumers today:

- `scripts/war-room-dashboard.ps1` — inline HTML, hand-rolled, brittle.
- `pl-engine/src/dashboard.py` — Excel templating tightly coupled to
  factory data.

Both rebuild from scratch every time, share no code, and look different.
Future consumers (BuildKit health, AI Ops audits, agentbridge
conformance reports, portfolio overview) need the same "data in →
polished dashboard out" pipeline.

This library is the shared substrate.

## Install

```bash
pip install -e ".[dev]"          # base + tests
pip install -e ".[all]"          # +excel, +pdf renderers
```

Excel needs `openpyxl`; PDF needs `weasyprint` (which has system deps on
Linux/macOS — on Windows it's pure-pip).

## 30-second tour

```python
from dashboards import Dashboard, render

dash = (
    Dashboard("War Room", subtitle="2026-05-04", theme="palantir")
    .section("Outreach")
        .kpi("Sends", 226, delta="+12")
        .kpi("Replies", 1, delta="+1")
    .section("Fleet")
        .table(
            headers=["Project", "Status", "Last Deploy"],
            rows=[
                ["operator-core", "GREEN", "2h ago"],
                ["ai-ops",        "RED",   "20d ago"],
            ],
        )
    .build()
)

html = render(dash, "html")          # str
md   = render(dash, "markdown")      # str
render(dash, "excel", out="war.xlsx")
render(dash, "pdf",   out="war.pdf")
```

## IR contract

The IR is JSON-schema-validated; see [`spec/DASHBOARD_SPEC.md`](spec/DASHBOARD_SPEC.md)
and [`spec/schema/v1/dashboard.json`](spec/schema/v1/dashboard.json).

Any structured data → IR → renderer. Add a renderer once, every
consumer gets it.

## CLI

```bash
dashboard render examples/war_room.json --format html  > war.html
dashboard render examples/pl_audit.json  --format excel --out audit.xlsx
```

## Layout

```
spec/                      DASHBOARD_SPEC.md + JSON Schema
src/dashboards/
  ir.py                    Pydantic IR types
  builder.py               fluent .section().kpi() API
  renderers/               html / markdown / excel / pdf
  components/              status_card, kpi_tile, table, timeline, callout
  themes/                  palantir, light  (CSS only)
examples/                  4 dashboards covering every component
tests/
cli/dashboard.py           thin argparse CLI
```

## Hard rules

1. Renderers are pure functions of IR. No side effects.
2. Adding a component type updates **all** renderers, or the renderer
   declares "html-only" (and the others render a `<callout>` saying so).
3. Themes are CSS only — no per-theme components.
4. ASCII-only Python source.
5. No `<script>` injection for arbitrary content; auto-escape.

## Status

| Phase | Item                          | State |
|-------|-------------------------------|-------|
| 1     | IR + JSON schema + Pydantic   | shipped |
| 2     | HTML renderer (Palantir)      | shipped |
| 3     | Markdown renderer             | shipped |
| 4     | Excel renderer                | shipped |
| 5     | PDF renderer                  | shipped |
| 6     | Builder API                   | shipped |
| 7     | Migrate war-room              | branch (visual review pending) |

See `CHANGELOG.md` for details.
