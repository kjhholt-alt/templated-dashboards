"""Theme registry. Themes are CSS strings keyed by name.

Renderers consume a theme name from the IR and resolve to CSS via
``get(name)``. Themes never carry component-specific Python.
"""

from __future__ import annotations

from . import palantir as _palantir
from . import light as _light

_THEMES = {
    "palantir": _palantir.CSS,
    "light": _light.CSS,
}


def get(name: str) -> str:
    return _THEMES.get(name, _palantir.CSS)


__all__ = ["get"]
