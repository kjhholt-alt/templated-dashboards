"""Renderer roundtrip + smoke tests.

Each renderer must accept the all-component IR and produce non-empty,
component-aware output. We don't snapshot byte-for-byte (themes evolve);
we check structural invariants.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from dashboards import Dashboard, load, render


def _full_dashboard():
    return (
        Dashboard("All", subtitle="every component", theme="palantir")
        .section("S")
            .status_card("p", inline_status={"tier": "good", "summary": "ok",
                                             "last_update": "2026-05-04"})
            .kpi("Sends", 226, delta="+12", tone="good")
            .kpi("Float", 12.5, tone="warn")
            .kpi("Str", "hello")
            .table(
                caption="cap",
                headers=["A", "B"],
                rows=[["1", "2"], [3, 4], ["x|y\n", None]],
            )
            .timeline([
                {"when": "now", "title": "t1", "tone": "good"},
                {"when": "later", "title": "t2", "detail": "d", "tone": "warn"},
            ])
            .callout("danger!", tone="bad", icon="!")
            .chart("bar", series=[
                {"label": "a", "points": [1.0, 2.0, 3.0]},
                {"label": "b", "points": [3.0, 2.0, 1.0]},
            ], caption="cap")
            .chart("line", series=[
                {"label": "single", "points": [1.0, 1.5, 0.5]},
            ])
        .footer("foot")
        .build()
    )


def test_html_smoke():
    dash = _full_dashboard()
    html = render(dash, "html")
    assert "<title>All</title>" in html
    assert 'class="dash"' in html
    assert "kpi-value" in html
    assert "status-card" in html
    assert "tbl" in html
    assert "timeline" in html
    assert "callout" in html
    assert "chart" in html
    # auto-escaping: pipe and newline cell got escaped, no raw <script>
    assert "<script" not in html or 'tailwindcss.com' in html  # tailwind allowed
    assert "x|y" in html or "x&#" in html


def test_html_escapes_user_content():
    dash = (
        Dashboard("Bad <script>")
        .section("S")
            .callout("<img src=x onerror=alert(1)>", tone="bad")
        .build()
    )
    out = render(dash, "html")
    # title appears escaped
    assert "Bad &lt;script&gt;" in out
    assert "&lt;img" in out
    # never raw injection
    assert "<img src=x onerror" not in out


def test_markdown_smoke():
    dash = _full_dashboard()
    md = render(dash, "markdown")
    assert md.startswith("# All\n")
    assert "## S" in md
    assert "**Sends**" in md
    assert "| A | B |" in md
    assert "[chart:bar]" in md  # chart fallback


def test_render_unknown_format_raises():
    from dashboards import UnsupportedRenderer

    dash = _full_dashboard()
    with pytest.raises(UnsupportedRenderer):
        render(dash, "xml")  # type: ignore[arg-type]


def test_render_writes_text_output(tmp_path: Path):
    dash = _full_dashboard()
    p = tmp_path / "x.html"
    out = render(dash, "html", out=p)
    assert out == p
    assert p.read_text(encoding="utf-8").startswith("<!doctype html>")


def test_render_excel_requires_out():
    dash = _full_dashboard()
    with pytest.raises(ValueError):
        render(dash, "excel")


def test_excel_renderer_smoke(tmp_path: Path):
    pytest.importorskip("openpyxl")
    dash = _full_dashboard()
    out = render(dash, "excel", out=tmp_path / "x.xlsx")
    assert out.exists()
    assert out.stat().st_size > 0


def test_pdf_renderer_smoke(tmp_path: Path):
    weasy = pytest.importorskip(
        "weasyprint", reason="weasyprint not installed; PDF test optional"
    ) if False else None
    try:
        import weasyprint  # noqa: F401
    except Exception:
        try:
            import reportlab  # noqa: F401
        except Exception:
            pytest.skip("neither weasyprint nor reportlab installed")
    dash = _full_dashboard()
    out = render(dash, "pdf", out=tmp_path / "x.pdf")
    assert out.exists()
    assert out.stat().st_size > 0


def test_load_then_render():
    """JSON-IR roundtrip through every text renderer."""
    raw = {
        "version": "1",
        "title": "T",
        "sections": [{
            "title": "S",
            "components": [{"type": "kpi_tile", "label": "X", "value": 1}],
        }],
    }
    dash = load(raw)
    assert "<title>T</title>" in render(dash, "html")
    assert "# T" in render(dash, "markdown")


def test_theme_light_renders():
    dash = (
        Dashboard("Lite", theme="light")
        .section("S").kpi("X", 1)
        .build()
    )
    html = render(dash, "html")
    assert "var(--fg-0)" in html  # css var present from theme


def _extras_dashboard():
    return (
        Dashboard("Extras", subtitle="pipeline + link_grid + code_block")
        .section("Funnel")
            .pipeline(
                [
                    {"name": "Lead", "value": 12, "state": "ready"},
                    {"name": "Approve", "value": 0, "state": "shipped"},
                    {"name": "Visit", "value": 220, "state": "watching"},
                    {"name": "Close", "value": 0, "state": "blocked"},
                ],
                caption="lead to close",
            )
        .section("Boards")
            .link_grid(
                [
                    {"label": "Mission Control", "href": "mc.html",
                     "kicker": "ops", "detail": "rollup view"},
                    {"label": "Trello", "href": "t.html", "tone": "good"},
                ],
                style="card",
                caption="quick boards",
            )
        .section("Quick links")
            .link_grid(
                [
                    {"label": "Runlog", "href": "RUNLOG.md", "ok": True},
                    {"label": "Missing", "href": "MISSING.md", "ok": False},
                ],
                style="chip",
            )
        .section("Diag")
            .code_block("M file.txt\n?? new.txt", language="diff",
                        caption="git status")
        .build()
    )


def test_pipeline_link_grid_code_block_html():
    dash = _extras_dashboard()
    html = render(dash, "html")
    # pipeline classes
    assert "pl-stage" in html
    assert "state-ready" in html
    assert "state-blocked" in html
    # link_grid card style
    assert "lg-card" in html
    # link_grid chip style with health badges
    assert "lg-chip ok" in html
    assert "lg-chip missing" in html
    assert "MISSING" in html
    # code block
    assert "<pre" in html
    assert "git status" in html


def test_pipeline_link_grid_code_block_markdown():
    dash = _extras_dashboard()
    md = render(dash, "markdown")
    assert "**Lead**" in md
    assert "[Runlog](RUNLOG.md)" in md
    assert "[OK]" in md
    assert "[MISSING]" in md
    assert "```diff" in md


def test_extras_excel_smoke(tmp_path: Path):
    pytest.importorskip("openpyxl")
    dash = _extras_dashboard()
    out = render(dash, "excel", out=tmp_path / "x.xlsx")
    assert out.exists() and out.stat().st_size > 0


def test_extras_load_validates():
    raw = {
        "version": "1",
        "title": "T",
        "sections": [{
            "title": "S",
            "components": [
                {
                    "type": "pipeline",
                    "stages": [
                        {"name": "A", "value": 1, "state": "ready"},
                        {"name": "B", "value": 2},
                    ],
                },
                {
                    "type": "link_grid",
                    "style": "chip",
                    "items": [
                        {"label": "X", "href": "x.html", "ok": True},
                    ],
                },
                {
                    "type": "code_block",
                    "text": "hello",
                },
            ],
        }],
    }
    dash = load(raw)
    out = render(dash, "html")
    assert "pl-stage" in out
    assert "lg-chip" in out
    assert "<pre" in out
