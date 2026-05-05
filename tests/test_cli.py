"""CLI tests."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from dashboards.cli import main as cli_main


def _ir_path(tmp_path: Path) -> Path:
    p = tmp_path / "ir.json"
    p.write_text(
        json.dumps({
            "version": "1",
            "title": "T",
            "sections": [{
                "title": "S",
                "components": [{"type": "kpi_tile", "label": "X", "value": 1}],
            }],
        }),
        encoding="utf-8",
    )
    return p


def test_cli_validate(tmp_path: Path, capsys):
    rc = cli_main(["validate", str(_ir_path(tmp_path))])
    assert rc == 0
    out = capsys.readouterr().out
    assert "OK:" in out


def test_cli_render_html(tmp_path: Path, capsys):
    rc = cli_main(["render", str(_ir_path(tmp_path)), "--format", "html"])
    assert rc == 0
    out = capsys.readouterr().out
    assert "<title>T</title>" in out


def test_cli_render_to_file(tmp_path: Path):
    p = _ir_path(tmp_path)
    out = tmp_path / "x.md"
    rc = cli_main(["render", str(p), "--format", "md", "--out", str(out)])
    assert rc == 0
    assert out.exists()
    assert out.read_text(encoding="utf-8").startswith("# T")


def test_cli_render_invalid_format(tmp_path: Path):
    with pytest.raises(SystemExit):
        cli_main(["render", str(_ir_path(tmp_path)), "--format", "xml"])
