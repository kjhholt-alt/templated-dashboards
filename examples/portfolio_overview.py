"""Portfolio overview — exercises status_card via inline_status."""

from __future__ import annotations

import json
import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE.parent / "src"))

from dashboards import Dashboard, render  # noqa: E402


def build():
    return (
        Dashboard("Portfolio Overview", subtitle="2026-05-04", theme="palantir")
        .section("Status", layout="grid")
            .status_card("operator-core", inline_status={
                "tier": "good", "summary": "watchdog 12s ago",
                "last_update": "2026-05-04T18:02Z",
            })
            .status_card("prospector-pro", inline_status={
                "tier": "good", "summary": "campaign factory deployed",
                "last_update": "2026-05-04T16:00Z",
            })
            .status_card("ai-ops-consulting", inline_status={
                "tier": "bad", "summary": "preview deploys ERROR (20d)",
                "last_update": "2026-05-04T17:55Z",
            })
            .status_card("pool-prospector", inline_status={
                "tier": "warn", "summary": "imagen quota at 80%",
                "last_update": "2026-05-04T17:00Z",
            })
        .section("Snapshot")
            .chart(
                "bar",
                series=[
                    {"label": "sends", "points": [12, 22, 38, 41, 26, 33, 54]},
                    {"label": "replies", "points": [0, 0, 0, 1, 0, 0, 0]},
                ],
                caption="Last 7 days",
            )
        .footer("internal — do not share")
        .build()
    )


def main():
    out_dir = _HERE.parent / "out"
    out_dir.mkdir(exist_ok=True)
    dash = build()
    (out_dir / "portfolio_overview.html").write_text(render(dash, "html"), encoding="utf-8")
    (out_dir / "portfolio_overview.json").write_text(
        json.dumps(dash.model_dump(exclude_none=True), indent=2),
        encoding="utf-8",
    )
    print(f"wrote {out_dir/'portfolio_overview.html'}")


if __name__ == "__main__":
    main()
