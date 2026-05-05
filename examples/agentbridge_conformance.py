"""agentbridge conformance report — exercises tables + callouts heavily."""

from __future__ import annotations

import json
import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE.parent / "src"))

from dashboards import Dashboard, render  # noqa: E402


def build():
    return (
        Dashboard(
            "agentbridge conformance",
            subtitle="protocol v1 / 2026-05-04 run",
            theme="palantir",
        )
        .section("Summary", layout="grid")
            .kpi("Tools tested", 24, tone="neutral")
            .kpi("Pass", 22, tone="good")
            .kpi("Fail", 1, tone="bad")
            .kpi("Skip", 1, tone="warn")
        .section("Per-tool results")
            .table(
                caption="Tool conformance",
                headers=["Tool", "Args OK", "Returns OK", "Notes"],
                rows=[
                    ["status.read",      "yes", "yes", ""],
                    ["events.append",    "yes", "yes", ""],
                    ["agent.spawn",      "yes", "no",  "missing trace_id in response"],
                    ["recipe.run",       "yes", "yes", ""],
                    ["fleet.snapshot",   "yes", "skip", "depends on real fleet, mocked"],
                ],
            )
        .section("Notes")
            .callout("agent.spawn — fix scheduled in operator-core 0.6.1", tone="warn")
            .callout("All other tools conform to protocol v1", tone="good")
        .footer("conformance run nightly via operator-core schedule")
        .build()
    )


def main():
    out_dir = _HERE.parent / "out"
    out_dir.mkdir(exist_ok=True)
    dash = build()
    (out_dir / "agentbridge_conformance.html").write_text(
        render(dash, "html"), encoding="utf-8"
    )
    (out_dir / "agentbridge_conformance.json").write_text(
        json.dumps(dash.model_dump(exclude_none=True), indent=2), encoding="utf-8"
    )
    print(f"wrote {out_dir/'agentbridge_conformance.html'}")


if __name__ == "__main__":
    main()
