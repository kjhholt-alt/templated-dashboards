"""PDF renderer.

Approach: render HTML (Tailwind off — print-friendly), feed to
weasyprint, write PDF. If weasyprint isn't available, fall back to a
plain-text PDF via reportlab if installed; otherwise raise a clear
``ImportError``.
"""

from __future__ import annotations

from pathlib import Path

from ..ir import Dashboard
from .html import render_html
from .markdown import render_markdown


def render_pdf(dash: Dashboard, out: Path) -> Path:
    out = Path(out)
    out.parent.mkdir(parents=True, exist_ok=True)

    # Try weasyprint first (highest fidelity). On Windows it often fails
    # at *load* time (missing pango/gobject), not just import — catch broadly.
    # weasyprint emits noisy stderr on partial install; silence it so the
    # fallback path is clean.
    import contextlib
    import io
    import os

    try:
        with contextlib.redirect_stderr(io.StringIO()):
            from weasyprint import HTML  # type: ignore

            html = render_html(dash, include_tailwind=False)
            HTML(string=html).write_pdf(target=str(out))
        return out
    except Exception:  # ImportError, OSError, etc.
        pass

    # Fallback: reportlab text-mode PDF using markdown rendering.
    try:
        from reportlab.lib.pagesizes import LETTER  # type: ignore
        from reportlab.pdfgen import canvas  # type: ignore
    except ImportError as e:  # pragma: no cover
        raise ImportError(
            "PDF rendering requires either weasyprint or reportlab. "
            "Install with: pip install templated-dashboards[pdf]"
        ) from e

    md = render_markdown(dash)
    c = canvas.Canvas(str(out), pagesize=LETTER)
    width, height = LETTER
    margin = 54  # 0.75 inch
    line_h = 12
    y = height - margin
    c.setFont("Courier", 10)
    for line in md.splitlines():
        if y < margin:
            c.showPage()
            c.setFont("Courier", 10)
            y = height - margin
        # rough wrap
        max_chars = 100
        while len(line) > max_chars:
            c.drawString(margin, y, line[:max_chars])
            line = line[max_chars:]
            y -= line_h
            if y < margin:
                c.showPage()
                c.setFont("Courier", 10)
                y = height - margin
        c.drawString(margin, y, line)
        y -= line_h
    c.save()
    return out


__all__ = ["render_pdf"]
