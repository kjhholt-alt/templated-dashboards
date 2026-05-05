"""Palantir / DoD-inspired dashboard theme.

Dark, monospaced, dense, no rounded corners. CSS-only. Designed to
play nice with Tailwind utility classes for layout while owning all
chrome / colour / typography.
"""

CSS = """
:root {
  --bg-0: #07090c;
  --bg-1: #0c1117;
  --bg-2: #111722;
  --bg-3: #182030;
  --line: #1f2a3b;
  --line-soft: #16202d;
  --fg-0: #e6edf3;
  --fg-1: #b3c1d1;
  --fg-2: #6f8197;
  --fg-3: #45596f;
  --accent: #38bdf8;
  --accent-2: #fbbf24;
  --good: #22c55e;
  --warn: #f59e0b;
  --bad:  #ef4444;
  --neutral: #94a3b8;
  --grid:    #0f1620;
}

* { box-sizing: border-box; }

html, body {
  background: var(--bg-0);
  color: var(--fg-0);
  font-family: ui-monospace, "SF Mono", "Cascadia Mono", Menlo,
               Consolas, "Liberation Mono", monospace;
  font-size: 13px;
  line-height: 1.45;
  margin: 0;
  padding: 0;
}

a { color: var(--accent); text-decoration: none; }
a:hover { text-decoration: underline; }

.dash {
  max-width: 1480px;
  margin: 0 auto;
  padding: 24px 28px 64px;
}

.dash-head {
  display: flex; flex-direction: column; gap: 4px;
  border-bottom: 1px solid var(--line);
  padding-bottom: 12px;
  margin-bottom: 24px;
}
.dash-title {
  font-size: 22px; letter-spacing: 0.04em;
  text-transform: uppercase; color: var(--fg-0);
  font-weight: 600;
}
.dash-subtitle {
  font-size: 12px; color: var(--fg-2);
  letter-spacing: 0.06em; text-transform: uppercase;
}

.section {
  margin-bottom: 32px;
  border-top: 1px solid var(--line-soft);
  padding-top: 16px;
}
.section-head {
  display: flex; align-items: baseline; gap: 12px;
  margin-bottom: 12px;
}
.section-title {
  font-size: 11px; letter-spacing: 0.18em;
  text-transform: uppercase; color: var(--fg-2);
}
.section-subtitle { font-size: 11px; color: var(--fg-3); }

.section-stack > * + * { margin-top: 12px; }
.section-grid {
  display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 12px;
}

/* status_card */
.status-card {
  display: grid; grid-template-columns: 12px 1fr auto;
  align-items: center; gap: 12px;
  background: var(--bg-1); border: 1px solid var(--line);
  padding: 12px 14px;
}
.status-card.tone-good { border-left: 3px solid var(--good); }
.status-card.tone-warn { border-left: 3px solid var(--warn); }
.status-card.tone-bad  { border-left: 3px solid var(--bad);  }
.status-card.tone-neutral { border-left: 3px solid var(--neutral); }
.status-dot { width: 10px; height: 10px; background: var(--neutral); }
.status-card.tone-good .status-dot { background: var(--good); }
.status-card.tone-warn .status-dot { background: var(--warn); }
.status-card.tone-bad  .status-dot { background: var(--bad); }
.status-body { display: flex; flex-direction: column; gap: 2px; }
.status-project {
  font-size: 13px; color: var(--fg-0); font-weight: 600;
  letter-spacing: 0.04em;
}
.status-summary { font-size: 11px; color: var(--fg-2); }
.status-meta { font-size: 10px; color: var(--fg-3); text-align: right; }

/* kpi_tile */
.kpi {
  background: var(--bg-1); border: 1px solid var(--line);
  padding: 14px 16px; display: flex; flex-direction: column; gap: 6px;
  min-height: 84px;
}
.kpi-label {
  font-size: 10px; color: var(--fg-2);
  text-transform: uppercase; letter-spacing: 0.16em;
}
.kpi-value {
  font-size: 28px; font-weight: 600; color: var(--fg-0);
  letter-spacing: 0.02em; line-height: 1;
}
.kpi-delta { font-size: 11px; color: var(--fg-2); }
.kpi.tone-good .kpi-value { color: var(--good); }
.kpi.tone-warn .kpi-value { color: var(--warn); }
.kpi.tone-bad  .kpi-value { color: var(--bad); }

/* table */
.tbl-wrap {
  background: var(--bg-1); border: 1px solid var(--line);
  overflow-x: auto;
}
.tbl-caption {
  font-size: 11px; color: var(--fg-2);
  text-transform: uppercase; letter-spacing: 0.14em;
  padding: 10px 14px; border-bottom: 1px solid var(--line-soft);
}
.tbl { width: 100%; border-collapse: collapse; }
.tbl th, .tbl td {
  padding: 8px 12px; text-align: left;
  border-bottom: 1px solid var(--line-soft);
  font-size: 12px;
}
.tbl th {
  font-size: 10px; color: var(--fg-2);
  text-transform: uppercase; letter-spacing: 0.12em;
  background: var(--bg-2);
  position: sticky; top: 0;
}
.tbl tr:hover td { background: var(--bg-2); }

/* timeline */
.timeline { display: flex; flex-direction: column; gap: 0; position: relative; }
.timeline::before {
  content: ""; position: absolute; left: 8px; top: 0; bottom: 0;
  width: 1px; background: var(--line);
}
.tl-event {
  display: grid; grid-template-columns: 24px 1fr;
  align-items: start; padding: 8px 0 8px 0;
}
.tl-marker {
  width: 9px; height: 9px; margin-top: 5px; margin-left: 4px;
  background: var(--neutral); border: 2px solid var(--bg-0);
  position: relative; z-index: 1;
}
.tl-event.tone-good .tl-marker { background: var(--good); }
.tl-event.tone-warn .tl-marker { background: var(--warn); }
.tl-event.tone-bad  .tl-marker { background: var(--bad); }
.tl-body { padding-left: 8px; }
.tl-when { font-size: 10px; color: var(--fg-3); letter-spacing: 0.1em;
           text-transform: uppercase; }
.tl-title { font-size: 13px; color: var(--fg-0); }
.tl-detail { font-size: 11px; color: var(--fg-2); }

/* callout */
.callout {
  display: grid; grid-template-columns: 22px 1fr;
  gap: 10px; padding: 10px 14px;
  background: var(--bg-1); border: 1px solid var(--line);
  border-left: 3px solid var(--neutral);
}
.callout.tone-good { border-left-color: var(--good); }
.callout.tone-warn { border-left-color: var(--warn); }
.callout.tone-bad  { border-left-color: var(--bad);  }
.callout-icon {
  font-weight: 700; color: var(--fg-2); text-align: center;
}
.callout-text { font-size: 12px; color: var(--fg-1); }

/* chart */
.chart {
  background: var(--bg-1); border: 1px solid var(--line);
  padding: 12px 14px;
}
.chart-caption {
  font-size: 10px; color: var(--fg-2);
  text-transform: uppercase; letter-spacing: 0.14em;
  margin-bottom: 8px;
}
.chart svg { display: block; width: 100%; height: 140px; }

/* footer */
.dash-footer {
  margin-top: 32px; padding-top: 12px;
  border-top: 1px solid var(--line);
  font-size: 10px; color: var(--fg-3);
  letter-spacing: 0.1em; text-transform: uppercase;
}

@media (max-width: 720px) {
  .dash { padding: 16px; }
  .section-grid { grid-template-columns: 1fr; }
  .kpi-value { font-size: 22px; }
}
"""
