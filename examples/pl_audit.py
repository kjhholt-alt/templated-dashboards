"""PL Audit — designed for the Excel renderer to produce manager-ready output.

Run:
    python examples/pl_audit.py            # writes html + xlsx
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE.parent / "src"))

from dashboards import Dashboard, render  # noqa: E402


def build():
    return (
        Dashboard("AX02 PL27 Audit", subtitle="period 5 close", theme="light")
        .section("Plan vs Actual")
            .kpi("Hours plan",    67043, tone="neutral")
            .kpi("Hours actual",  62110, delta="-4,933", tone="warn")
            .kpi("CPOH plan",     "$118.40")
            .kpi("CPOH actual",   "$121.05", delta="+$2.65", tone="warn")
        .section("Variance by account")
            .table(
                caption="Top 5 unfavorable accounts (period 5)",
                headers=["Account", "Plan", "Actual", "Var", "% Var"],
                rows=[
                    ["503100 Direct Wages",   320000, 341200,  -21200, "-6.6%"],
                    ["541000 Indirect Wages", 178000, 192100,  -14100, "-7.9%"],
                    ["523200 Repairs",         48000,  61400,  -13400, "-27.9%"],
                    ["552000 Energy",          24000,  29900,   -5900, "-24.6%"],
                    ["531000 Supplies",        38000,  42100,   -4100, "-10.8%"],
                ],
            )
        .section("Trend")
            .chart(
                "line",
                series=[
                    {"label": "CPOH plan",   "points": [118, 118, 118, 118, 118]},
                    {"label": "CPOH actual", "points": [115, 119, 122, 124, 121]},
                ],
                caption="CPOH by period (period 1-5)",
            )
        .section("Notes")
            .callout("Indirect wage drift driven by overtime in CC 4302", tone="warn")
            .callout("Repairs spike: dryer #2 drive replacement, one-off", tone="neutral")
        .footer("AX02 finance / PL Engine")
        .build()
    )


def main():
    out_dir = _HERE.parent / "out"
    out_dir.mkdir(exist_ok=True)
    dash = build()
    (out_dir / "pl_audit.html").write_text(render(dash, "html"), encoding="utf-8")
    (out_dir / "pl_audit.json").write_text(
        json.dumps(dash.model_dump(exclude_none=True), indent=2), encoding="utf-8"
    )
    try:
        render(dash, "excel", out=out_dir / "pl_audit.xlsx")
        print(f"wrote {out_dir/'pl_audit.xlsx'}")
    except ImportError as e:
        print(f"skip excel: {e}")
    print(f"wrote {out_dir/'pl_audit.html'}")


if __name__ == "__main__":
    main()
