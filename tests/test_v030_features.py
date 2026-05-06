"""Tests for v0.3.0 lib gap closures.

Covers:
- Cover-page component across HTML / Markdown / Excel (PDF inherits HTML).
- ROI summary component across HTML / Markdown / Excel.
- KPI grid layouts in HTML + Excel (column-aware).
- Per-cell tone hints on tables in HTML + Excel.
- Playwright PDF backend probe (graceful fallback when not installed).

Existing v0.2.0 tests must still pass — see test_renderers.py / test_ir.py.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from dashboards import Dashboard, render
from dashboards.ir import (
    CoverPage,
    ROISummary,
    Table,
    Section,
    Dashboard as IRDashboard,
    load,
    dump,
)


# ---------------------------------------------------------------------------
# Cover page
# ---------------------------------------------------------------------------


def _cover_dash() -> Dashboard:
    return (
        Dashboard("Test deliverable", subtitle="Tier 1 audit")
        .section("Cover", layout="stack")
        .cover_page(
            "Acme Audit Report",
            subtitle="Operational AI assessment",
            prepared_for="Acme Corp -- Sarah Lee",
            prepared_by="BuildKit Operator -- 2026-05-06",
            version="v1.0.0",
            logo_initials="BK",
        )
    )


def test_cover_page_ir_validates() -> None:
    """Cover page round-trips through IR + JSON Schema."""
    d = _cover_dash().build()
    raw = d.model_dump(exclude_none=True)
    loaded = load(dump(d))
    assert loaded.sections[0].components[0].title == "Acme Audit Report"
    assert raw["sections"][0]["components"][0]["type"] == "cover_page"


def test_cover_page_html_renders() -> None:
    html = render(_cover_dash().build(), "html")
    assert "Acme Audit Report" in html
    assert "Operational AI assessment" in html
    assert "PREPARED FOR" in html
    assert "PREPARED BY" in html
    assert "VERSION" in html
    assert "v1.0.0" in html
    assert ">BK<" in html  # logo initials rendered


def test_cover_page_markdown_renders() -> None:
    md = render(_cover_dash().build(), "markdown")
    assert "# Acme Audit Report" in md
    assert "_Operational AI assessment_" in md
    assert "Acme Corp -- Sarah Lee" in md
    assert "BuildKit Operator -- 2026-05-06" in md
    assert "v1.0.0" in md


def test_cover_page_excel_renders(tmp_path: Path) -> None:
    out = tmp_path / "cover.xlsx"
    render(_cover_dash().build(), "excel", out=out)
    assert out.exists() and out.stat().st_size > 0


def test_cover_page_minimal_only_title() -> None:
    """Only title is required."""
    d = (
        Dashboard("X")
        .section("S")
        .cover_page("Just a title")
        .build()
    )
    html = render(d, "html")
    assert "Just a title" in html


# ---------------------------------------------------------------------------
# ROI summary
# ---------------------------------------------------------------------------


def _roi_dash() -> Dashboard:
    return (
        Dashboard("ROI test")
        .section("ROI", layout="stack")
        .roi_summary(
            investment_usd=3500,
            monthly_recovery_usd=14400,
            annual_recovery_usd=172800,
            multiplier="44x",
            payback_months=0.24,
        )
    )


def test_roi_summary_ir_validates() -> None:
    d = _roi_dash().build()
    loaded = load(dump(d))
    assert loaded.sections[0].components[0].multiplier == "44x"


def test_roi_summary_html_emphasizes_multiplier() -> None:
    html = render(_roi_dash().build(), "html")
    # Multiplier is the loud element
    assert "44x" in html
    assert "INVESTMENT" in html
    assert "MONTHLY RECOVERY" in html
    assert "ANNUAL RECOVERY" in html
    assert "PAYBACK" in html
    # USD values formatted
    assert "$3,500" in html
    assert "$14,400" in html


def test_roi_summary_markdown_renders() -> None:
    md = render(_roi_dash().build(), "markdown")
    assert "44x ROI" in md
    assert "$172,800" in md
    assert "0.2 months" in md


def test_roi_summary_excel_renders(tmp_path: Path) -> None:
    out = tmp_path / "roi.xlsx"
    render(_roi_dash().build(), "excel", out=out)
    assert out.exists() and out.stat().st_size > 0


# ---------------------------------------------------------------------------
# KPI grid layouts
# ---------------------------------------------------------------------------


def _kpi_grid_dash(cols: int) -> Dashboard:
    layout = f"kpi_grid_{cols}col"
    return (
        Dashboard("KPI grid test")
        .section("Quarterlies", layout=layout)
        .kpi("Q1", 100)
        .kpi("Q2", 200)
        .kpi("Q3", 300)
        .kpi("Q4", 400)
    )


def test_kpi_grid_2col_layout_validates() -> None:
    d = _kpi_grid_dash(2).build()
    loaded = load(dump(d))
    assert loaded.sections[0].layout == "kpi_grid_2col"


def test_kpi_grid_html_uses_section_kpi_grid_class() -> None:
    html = render(_kpi_grid_dash(3).build(), "html")
    assert "section-kpi-grid" in html
    assert "section-kpi-grid-3" in html


def test_kpi_grid_excel_renders_without_collapse(tmp_path: Path) -> None:
    """Excel renderer accepts kpi_grid layouts without crashing."""
    out = tmp_path / "kpi_grid.xlsx"
    render(_kpi_grid_dash(2).build(), "excel", out=out)
    assert out.exists() and out.stat().st_size > 0


def test_kpi_grid_invalid_layout_rejected() -> None:
    """Schema rejects unknown layouts."""
    with pytest.raises(Exception):
        d_dict = {
            "version": "1",
            "title": "x",
            "sections": [
                {
                    "title": "x",
                    "layout": "kpi_grid_99col",
                    "components": [{"type": "kpi_tile", "label": "x", "value": 1}],
                }
            ],
        }
        load(d_dict)


# ---------------------------------------------------------------------------
# Per-cell tone hints
# ---------------------------------------------------------------------------


def _cell_tones_dash() -> Dashboard:
    return (
        Dashboard("Cell tones test")
        .section("Findings")
        .table(
            headers=["Finding", "Severity", "Effort"],
            rows=[
                ["Manual lead intake", "high", "low"],
                ["No CRM sync", "med", "med"],
                ["Stale dashboards", "low", "low"],
            ],
            cell_tones=[
                [None, "bad", "good"],
                [None, "warn", "warn"],
                [None, "neutral", "good"],
            ],
        )
    )


def test_cell_tones_ir_validates() -> None:
    d = _cell_tones_dash().build()
    loaded = load(dump(d))
    table = loaded.sections[0].components[0]
    assert isinstance(table, Table)
    assert table.cell_tones[0][1] == "bad"
    assert table.cell_tones[2][2] == "good"


def test_cell_tones_html_applies_tone_class() -> None:
    html = render(_cell_tones_dash().build(), "html")
    assert 'class="tone-bad"' in html
    assert 'class="tone-good"' in html
    assert 'class="tone-warn"' in html


def test_cell_tones_excel_renders(tmp_path: Path) -> None:
    out = tmp_path / "tones.xlsx"
    render(_cell_tones_dash().build(), "excel", out=out)
    assert out.exists() and out.stat().st_size > 0


def test_cell_tones_markdown_ignores_tones() -> None:
    """Markdown ignores tones (plain text). Output should still contain
    the cell text."""
    md = render(_cell_tones_dash().build(), "markdown")
    assert "Manual lead intake" in md
    assert "Stale dashboards" in md


def test_cell_tones_optional_backwards_compat() -> None:
    """A table without cell_tones still renders fine (v0.2.0 callers)."""
    d = (
        Dashboard("Old caller test")
        .section("Plain")
        .table(headers=["a", "b"], rows=[["1", "2"], ["3", "4"]])
        .build()
    )
    html = render(d, "html")
    # No tone classes should appear
    assert 'class="tone-' not in html
    # Cells still rendered
    assert "<td>1</td>" in html


def test_cell_tones_shorter_row_padded_with_none() -> None:
    """If cell_tones row is shorter than data row, missing entries treated as None."""
    d = (
        Dashboard("Short tones test")
        .section("Pad")
        .table(
            headers=["a", "b", "c"],
            rows=[["1", "2", "3"]],
            cell_tones=[["good"]],  # only first cell has tone
        )
        .build()
    )
    html = render(d, "html")
    assert 'class="tone-good"' in html
    # The other cells should NOT have a tone class
    assert html.count('class="tone-') == 1


# ---------------------------------------------------------------------------
# PDF playwright backend probe (graceful fallback)
# ---------------------------------------------------------------------------


def test_pdf_render_succeeds_with_some_backend(tmp_path: Path) -> None:
    """PDF render must succeed -- whichever backend wins (playwright,
    weasyprint, or reportlab fallback). Just check the file is non-empty."""
    d = _cover_dash().build()
    out = tmp_path / "out.pdf"
    render(d, "pdf", out=out)
    assert out.exists()
    assert out.stat().st_size > 0


def test_pdf_render_handles_v030_components(tmp_path: Path) -> None:
    """PDF must not crash on the new components."""
    d = (
        Dashboard("PDF v0.3.0 test")
        .section("Cover")
        .cover_page("Title", prepared_for="X", prepared_by="Y")
        .section("ROI")
        .roi_summary(
            investment_usd=1000,
            monthly_recovery_usd=500,
            annual_recovery_usd=6000,
            multiplier="6x",
            payback_months=2.0,
        )
        .section("Results", layout="kpi_grid_2col")
        .kpi("a", 1)
        .kpi("b", 2)
        .build()
    )
    out = tmp_path / "v030.pdf"
    render(d, "pdf", out=out)
    assert out.exists() and out.stat().st_size > 0
