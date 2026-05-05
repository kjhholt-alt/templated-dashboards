"""chart shared helpers."""

from __future__ import annotations

from ..ir import Chart


def all_points(c: Chart) -> list[float]:
    out: list[float] = []
    for s in c.series:
        out.extend(s.points)
    return out


def y_range(c: Chart) -> tuple[float, float]:
    pts = all_points(c)
    if not pts:
        return 0.0, 1.0
    lo, hi = min(pts), max(pts)
    if lo == hi:
        return lo - 1.0, hi + 1.0
    return lo, hi


__all__ = ["all_points", "y_range"]
