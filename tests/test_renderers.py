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
