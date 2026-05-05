"""IR + JSON-Schema validation tests."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from dashboards import Dashboard, DashboardIR, dump, load


def _minimal_ir() -> dict:
    return {
        "version": "1",
        "title": "Demo",
        "sections": [
            {"title": "S", "components": [
                {"type": "kpi_tile", "label": "X", "value": 1},
            ]},
        ],
    }


def test_load_minimal_ir():
    d = load(_minimal_ir())
    assert isinstance(d, DashboardIR)
    assert d.title == "Demo"
    assert d.sections[0].components[0].value == 1


def test_load_rejects_unknown_field():
    bad = _minimal_ir()
    bad["nope"] = "yes"
    with pytest.raises(Exception):
        load(bad)


def test_load_requires_at_least_one_section():
    bad = {"version": "1", "title": "Demo", "sections": []}
    with pytest.raises(Exception):
        load(bad)


def test_load_section_requires_components():
    bad = {
        "version": "1",
        "title": "Demo",
        "sections": [{"title": "S", "components": []}],
    }
    with pytest.raises(Exception):
        load(bad)


def test_dump_roundtrip():
    d = load(_minimal_ir())
    s = dump(d)
    raw = json.loads(s)
    assert raw["title"] == "Demo"
    assert raw["sections"][0]["components"][0]["type"] == "kpi_tile"


def test_load_from_path(tmp_path: Path):
    p = tmp_path / "ir.json"
    p.write_text(json.dumps(_minimal_ir()), encoding="utf-8")
    d = load(p)
    assert d.title == "Demo"


def test_examples_validate():
    """All four example dashboards must produce valid IR."""
    import importlib.util

    here = Path(__file__).resolve().parent
    examples_dir = here.parent / "examples"
    for name in (
        "war_room",
        "portfolio_overview",
        "agentbridge_conformance",
        "pl_audit",
    ):
        spec = importlib.util.spec_from_file_location(
            name, examples_dir / f"{name}.py"
        )
        assert spec is not None and spec.loader is not None
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        dash = mod.build()
        # Re-validate via load() on dumped form
        load(dash.model_dump(exclude_none=True))


def test_all_components_in_one_dashboard():
    ir = {
        "version": "1",
        "title": "All",
        "sections": [{
            "title": "S",
            "components": [
                {"type": "status_card", "project": "p",
                 "inline_status": {"tier": "good", "summary": "ok"}},
                {"type": "kpi_tile", "label": "L", "value": 1, "tone": "good"},
                {"type": "table", "headers": ["A"], "rows": [["1"]]},
                {"type": "timeline", "events": [
                    {"when": "now", "title": "t"},
                ]},
                {"type": "callout", "text": "hi", "tone": "warn"},
                {"type": "chart", "kind": "bar", "series": [
                    {"label": "x", "points": [1, 2, 3]},
                ]},
            ],
        }],
    }
    d = load(ir)
    types = [c.type for c in d.sections[0].components]
    assert types == [
        "status_card", "kpi_tile", "table", "timeline", "callout", "chart"
    ]
