"""Render dispatcher: IR -> output by format name."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Optional, Union

from .ir import Dashboard, load


class UnsupportedRenderer(Exception):
    """Raised when an unknown format is requested."""


class UnsupportedComponent(Exception):
    """Raised by a renderer when it cannot represent a component type."""


_FORMATS = {"html", "markdown", "md", "excel", "xlsx", "pdf"}


def render(
    dashboard: Union[Dashboard, dict, str, Path],
    fmt: str,
    *,
    out: Optional[Union[str, Path]] = None,
    **kwargs: Any,
) -> Any:
    """Render a Dashboard IR to a given format.

    Args:
        dashboard: IR Dashboard, dict, JSON string, or path.
        fmt: one of ``html``, ``markdown`` (alias ``md``),
             ``excel`` (alias ``xlsx``), ``pdf``.
        out: optional output path. For text formats (html, md), if
             provided the file is written and the path returned.
             For binary formats (xlsx, pdf), this is required.
        **kwargs: passed through to the renderer.

    Returns:
        For text formats: the rendered string (or path if ``out`` given).
        For binary formats: the path written to.
    """
    fmt = fmt.lower()
    if fmt not in _FORMATS:
        raise UnsupportedRenderer(f"unknown format: {fmt}")

    if not isinstance(dashboard, Dashboard):
        dashboard = load(dashboard)

    if fmt == "html":
        from .renderers.html import render_html

        text = render_html(dashboard, **kwargs)
        if out:
            Path(out).write_text(text, encoding="utf-8")
            return Path(out)
        return text

    if fmt in ("markdown", "md"):
        from .renderers.markdown import render_markdown

        text = render_markdown(dashboard, **kwargs)
        if out:
            Path(out).write_text(text, encoding="utf-8")
            return Path(out)
        return text

    if fmt in ("excel", "xlsx"):
        from .renderers.excel import render_excel

        if not out:
            raise ValueError("excel renderer requires an `out` path")
        return render_excel(dashboard, Path(out), **kwargs)

    if fmt == "pdf":
        from .renderers.pdf import render_pdf

        if not out:
            raise ValueError("pdf renderer requires an `out` path")
        return render_pdf(dashboard, Path(out), **kwargs)

    raise UnsupportedRenderer(f"unhandled format: {fmt}")  # pragma: no cover


__all__ = ["render", "UnsupportedRenderer", "UnsupportedComponent"]
