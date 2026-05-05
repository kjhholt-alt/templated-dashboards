"""Status-spec stub + status_card resolution tests."""

from __future__ import annotations

import json
from pathlib import Path

from dashboards._status_stub import read_status
from dashboards.components.status_card import resolve
from dashboards.ir import StatusCard


def test_read_status_missing(tmp_path: Path):
    out = read_status(str(tmp_path / "nope.json"))
    assert out["tier"] == "neutral"


def test_read_status_url_blocked():
    out = read_status("https://example.com/status.json")
    assert out["tier"] == "neutral"
    assert "stub" in out["summary"]


def test_read_status_local(tmp_path: Path):
    p = tmp_path / "s.json"
    p.write_text(json.dumps({
        "tier": "GREEN", "summary": "ok", "last_update": "today",
    }))
    out = read_status(str(p))
    assert out["tier"] == "GREEN"


def test_resolve_inline_normalises_green_to_good():
    sc = StatusCard(project="p", inline_status={"tier": "GREEN"})
    r = resolve(sc)
    assert r["tier"] == "good"


def test_resolve_inline_normalises_red():
    sc = StatusCard(project="p", inline_status={"status": "red", "note": "oh"})
    r = resolve(sc)
    assert r["tier"] == "bad"
    assert r["summary"] == "oh"


def test_resolve_unknown_tier_neutral():
    sc = StatusCard(project="p", inline_status={"tier": "blue"})
    r = resolve(sc)
    assert r["tier"] == "neutral"


def test_resolve_no_status_at_all():
    sc = StatusCard(project="p")
    r = resolve(sc)
    assert r["tier"] == "neutral"
    assert r["project"] == "p"


def test_resolve_status_url(tmp_path: Path):
    p = tmp_path / "s.json"
    p.write_text(json.dumps({"tier": "warn", "summary": "degraded"}))
    sc = StatusCard(project="p", status_url=str(p))
    r = resolve(sc)
    assert r["tier"] == "warn"
    assert r["summary"] == "degraded"
