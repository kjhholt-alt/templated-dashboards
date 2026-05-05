"""kpi_tile shared helpers."""

from __future__ import annotations

from ..ir import KPITile


def format_value(tile: KPITile) -> str:
    v = tile.value
    if isinstance(v, float):
        if v.is_integer():
            return f"{int(v):,}"
        return f"{v:,.2f}"
    if isinstance(v, int):
        return f"{v:,}"
    return str(v)


__all__ = ["format_value"]
