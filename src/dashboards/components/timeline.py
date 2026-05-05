"""timeline shared helpers."""

from __future__ import annotations

from ..ir import Timeline


def by_when(t: Timeline) -> list:
    """Return events in input order; here for symmetry / future hooks."""
    return list(t.events)


__all__ = ["by_when"]
