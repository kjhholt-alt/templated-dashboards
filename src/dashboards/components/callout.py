"""callout shared helpers."""

from __future__ import annotations

from ..ir import Callout


def icon_for(c: Callout) -> str:
    if c.icon:
        return c.icon
    return {
        "good": "+",
        "warn": "!",
        "bad": "x",
        "neutral": "i",
    }.get(c.tone, "i")


__all__ = ["icon_for"]
