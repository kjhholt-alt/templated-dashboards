# Changelog

## 0.1.0 — 2026-05-04

Initial release.

### Phase 1 — IR + schema
- `spec/DASHBOARD_SPEC.md` v1
- `spec/schema/v1/dashboard.json` (JSON Schema 2020-12)
- Pydantic IR types in `dashboards.ir` with strict (extra=forbid) models
- 4 example dashboards (war_room, portfolio_overview,
  agentbridge_conformance, pl_audit) all validate

### Phase 2 — HTML renderer
- Palantir theme (dark, monospaced, dense, no rounded corners)
- Light theme (printable variant)
- All 6 components (status_card, kpi_tile, table, timeline, callout, chart)
- Tailwind CDN included for utility classes; no build step
- Auto-escape via `html.escape` everywhere
- Inline SVG charts (bar / line / sparkline)

### Phase 3 — Markdown renderer
- CommonMark-friendly output for terminal / Discord
- Charts degrade to a callout note ("chart omitted in markdown")

### Phase 4 — Excel renderer (openpyxl)
- Title + subtitle merged header row
- KPI tiles as 2x2 blocks with tone colour fills
- Tables with frozen header row and bordered rows
- Timeline as ordered rows with tone marker cell
- Callouts as merged-row blocks with tone left bar
- Charts: openpyxl native BarChart / LineChart embedded next to data

### Phase 5 — PDF renderer
- weasyprint primary path (HTML reuse)
- reportlab fallback (Courier text mode) when weasyprint can't load
  system libs (common on Windows)
- Stderr from weasyprint silenced on the fallback path

### Phase 6 — Builder API
- Fluent `Dashboard("Title").section(...).kpi(...).table(...).build()`
- All 6 component shorthands wired
- `to_dict()` for JSON serialisation
- Validation deferred to `.build()`

### Phase 7 — Migrate war-room (BRANCH WORK)
- Builder `examples/war_room.py` produces the new layout
- Branch `templated-dashboards/war-room-rebuild` in projects repo
  vendors a thin wrapper at `scripts/war-room-dashboard.py`
- Old `scripts/war-room-dashboard.ps1` left intact for visual diff /
  rollback. **Visual review pending** before old script removal.

### Tests
- 36 tests across 5 files (test_ir, test_renderers, test_builder,
  test_status_stub, test_cli)
- Direct test runner at `tests/_run_direct.py` for environments where
  pytest output capture misbehaves
- All tests pass under both pytest and the direct runner

### Known gaps
- Coverage gate (`>=85%`) not yet wired into CI; tests cover all
  shipped renderers and the builder. Coverage measurement is in the
  pyproject; running `pytest --cov` works locally.
- weasyprint Windows install: requires GTK/pango. If absent, PDF
  output falls back to reportlab (text-mode) automatically.
