"""Builder API tests."""

from __future__ import annotations

import pytest

from dashboards import Dashboard, DashboardIR, load


def test_builder_basic():
    d = (
        Dashboard("X", subtitle="s")
        .section("A")
            .kpi("k", 1)
        .section("B")
            .callout("hi")
        .footer("f")
        .build()
    )
    assert isinstance(d, DashboardIR)
    assert len(d.sections) == 2
    assert d.sections[0].title == "A"
    assert d.sections[1].components[0].type == "callout"
    assert d.footer == "f"


def test_builder_requires_section_first():
    with pytest.raises(RuntimeError):
        Dashboard("X").kpi("k", 1)


def test_builder_to_dict_roundtrip():
    d = (
        Dashboard("X")
        .section("S")
            .kpi("k", 2)
            .table(headers=["A"], rows=[["1"]])
        .build()
    )
    raw = d.model_dump(exclude_none=True)
    again = load(raw)
    assert again.title == "X"
    assert again.sections[0].components[1].type == "table"


def test_builder_chart_and_timeline():
    d = (
        Dashboard("X")
        .section("S")
            .timeline([{"when": "now", "title": "t"}])
            .chart("line", series=[{"label": "a", "points": [1.0, 2.0]}])
        .build()
    )
    assert d.sections[0].components[0].type == "timeline"
    assert d.sections[0].components[1].type == "chart"


def test_builder_status_card_inline():
    d = (
        Dashboard("X").section("S")
        .status_card("p", inline_status={"tier": "good"})
        .build()
    )
    sc = d.sections[0].components[0]
    assert sc.project == "p"
    assert sc.inline_status == {"tier": "good"}


def test_builder_grid_layout():
    d = Dashboard("X").section("S", layout="grid").kpi("k", 1).build()
    assert d.sections[0].layout == "grid"
