"""PDF renderer.

v0.3.0 strategy: prefer Chromium-via-playwright for browser-grade fidelity
(works on Windows out of the box once ``python -m playwright install
chromium`` has been run). Fall through to weasyprint, then to a plain-text
reportlab PDF, then raise a clear ``ImportError``.

Order of attempts:

1. **playwright (sync API)** -- highest fidelity. Identical to "print to PDF"
   from a real browser. Renders the same HTML the HTML renderer produces.
2. **weasyprint** -- works on Linux / Mac with pango/gobject installed.
   Often fails on Windows at load time even when import succeeds.
3. **reportlab** -- absolute fallback. Plain Courier text, but at least the
   pipeline doesn't crash.

All three paths render the same Dashboard input, so callers don't need to
care which backend won.
"""

from __future__ import annotations

import contextlib
import io
from pathlib import Path

from ..ir import Dashboard
from .html import render_html
from .markdown import render_markdown


def render_pdf(dash: Dashboard, out: Path) -> Path:
    out = Path(out)
    out.parent.mkdir(parents=True, exist_ok=True)

    # 1. Playwright (Chromium HTML -> PDF). Best fidelity. On first run
    #    the user must `python -m playwright install chromium`. We capture
    #    the launch failure and fall through silently if so.
    if _try_playwright(dash, out):
        return out

    # 2. Weasyprint. Suppress its stderr noise on partial installs so the
    #    fallback path stays readable.
    if _try_weasyprint(dash, out):
        return out

    # 3. Reportlab plain-text. Last resort.
    return _emit_reportlab(dash, out)


# ---------------------------------------------------------------------------
# Backend probes
# ---------------------------------------------------------------------------


def _try_playwright(dash: Dashboard, out: Path) -> bool:
    """Render via Chromium. Returns True if the PDF was written."""
    try:
        with contextlib.redirect_stderr(io.StringIO()):
            from playwright.sync_api import sync_playwright  # type: ignore
    except ImportError:
        return False
    try:
        html = render_html(dash, include_tailwind=True)
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()
            page.set_content(html, wait_until="networkidle")
            page.pdf(
                path=str(out),
                format="Letter",
                print_background=True,
                margin={"top": "0.5in", "bottom": "0.5in", "left": "0.5in", "right": "0.5in"},
            )
            browser.close()
        return out.exists() and out.stat().st_size > 0
    except Exception:  # noqa: BLE001 -- launch errors, missing chromium binary
        return False


def _try_weasyprint(dash: Dashboard, out: Path) -> bool:
    try:
        with contextlib.redirect_stderr(io.StringIO()):
            from weasyprint import HTML  # type: ignore

            html = render_html(dash, include_tailwind=False)
            HTML(string=html).write_pdf(target=str(out))
        return out.exists() and out.stat().st_size > 0
    except Exception:  # noqa: BLE001 -- ImportError or OSError
        return False


def _emit_reportlab(dash: Dashboard, out: Path) -> Path:
    try:
        from reportlab.lib.pagesizes import LETTER  # type: ignore
        from reportlab.pdfgen import canvas  # type: ignore
    except ImportError as e:  # pragma: no cover
        raise ImportError(
            "PDF rendering requires playwright (preferred) or weasyprint or "
            "reportlab. Install with: pip install templated-dashboards[pdf] "
            "and run: python -m playwright install chromium"
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
