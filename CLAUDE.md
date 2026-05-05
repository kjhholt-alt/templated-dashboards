# templated-dashboards — Claude context

This is a templating library, NOT an app. Don't add a server, a UI, or
business logic. The whole point is "data → multiple polished outputs."

## Architecture in one breath

`IR (pydantic) -> renderer (html|markdown|excel|pdf) -> output`

The IR is the contract. Renderers are pure functions of IR. Themes are
CSS only. Components live in one place and every renderer must support
them (or document the omission).

## Adding a component type — checklist

1. `src/dashboards/components/<name>.py` — pydantic model + `kind`
   literal in `ir.Component`.
2. `spec/schema/v1/dashboard.json` — extend the `oneOf`.
3. `spec/DASHBOARD_SPEC.md` — describe the component.
4. **All four renderers** — html, markdown, excel, pdf — implement it
   OR raise `UnsupportedComponent` so callers know.
5. Test: roundtrip JSON IR through every renderer, snapshot output
   under `tests/snapshots/<component>/<format>.{html,md,xlsx,pdf}`.
6. Builder API: add a `dash.section(...).<name>(...)` shorthand if
   ergonomic.

## Hard rules (do not break)

- ASCII-only Python source.
- No `<script>` injection — `html.escape` everywhere.
- Renderers cannot import from each other.
- Themes are CSS strings; never component-specific Python.
- Conventional commits with `Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>`.

## Status-spec stub

If `status-spec` (sibling library) isn't published yet, we vendor a
minimal stub at `src/dashboards/_status_stub/` that mirrors its
`read_status(path) -> StatusCard` API. Replace with the real package
when it ships.

## Don't

- Don't fetch data inside a renderer. Caller pre-resolves status files
  / counts / etc. into the IR.
- Don't build a frontend framework. HTML output uses Tailwind CDN, no
  build step.
- Don't couple to PL-engine, war-room, or any specific consumer.

## When stuck

Re-read `spec/DASHBOARD_SPEC.md`. The IR is the contract; everything
else is implementation.
