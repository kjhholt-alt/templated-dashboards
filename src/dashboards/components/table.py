"""table shared helpers."""

from __future__ import annotations

from ..ir import Table


def normalise_rows(t: Table) -> list[list[str]]:
    """Pad / truncate rows to header width and stringify cells."""
    width = len(t.headers)
    out: list[list[str]] = []
    for row in t.rows:
        cells = ["" if c is None else str(c) for c in row[:width]]
        if len(cells) < width:
            cells.extend([""] * (width - len(cells)))
        out.append(cells)
    return out


__all__ = ["normalise_rows"]
