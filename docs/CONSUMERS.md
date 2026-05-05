# Consumers

Real / planned consumers of `templated-dashboards`. When you wire up a
new one, add it here with a one-liner about what it builds.

## Active

| Consumer | What it builds | Format |
|----------|----------------|--------|
| `scripts/war-room-dashboard.py` (Phase 7) | Daily portfolio status (was the 1753-line PS1) | HTML |
| `pl-engine` (planned) | AX02 PL27 audit deck | Excel |

## Planned

| Consumer | What it would build |
|----------|---------------------|
| BuildKit health | Status of cron + bot + S1API + Imagen quotas |
| AI Ops audits | $3,500 deliverables — PDF |
| agentbridge conformance | Nightly conformance report — HTML + Markdown |
| Portfolio overview | Cross-product KPIs — HTML |

## Adding a consumer

1. Build a Pydantic IR with the fluent builder OR write the JSON
   directly. Either way, the IR is the contract.
2. Call `dashboards.render(dash, "<format>")`.
3. If your consumer needs status-card data, it must pre-resolve into
   `inline_status={...}` OR pass `status_url=` to a local file the
   stub can read.
4. Don't add a renderer-side dependency on your data shape. If a
   component is missing for your use case, add it to the IR (and to
   all four renderers).
