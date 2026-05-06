# Changelog

## 0.3.0 — 2026-05-06

### New components

- **`cover_page`** — first-class deliverable cover. Big title + subtitle,
  optional logo initials, prepared-for / prepared-by / version meta block.
  Built for AI Ops audit deliverables and Pool Prospector postcards.
  Renders in HTML (banded header card), Markdown (# title + key-value
  block), Excel (top-of-sheet styled band), PDF (inherits HTML via the
  new playwright path).
- **`roi_summary`** — investment + monthly recovery + annual recovery +
  multiplier (loud) + payback months. Replaces hand-rolled ROI callouts.
  All four renderers support it.

### New table feature

- **`cell_tones`** — optional per-cell tone hints. Same shape as `rows`
  (or sparser); each cell tagged `good`/`warn`/`bad`/`neutral` gets the
  matching color treatment. HTML applies a `tone-*` class; Excel applies
  a fill; Markdown ignores; PDF inherits from HTML. Backwards-compatible
  for v0.2.0 callers (omit the param, no behaviour change).

### New section layouts

- **`kpi_grid_2col` / `kpi_grid_3col` / `kpi_grid_4col`** — print-aware
  fixed-column KPI grids. Solves the v0.2.0 issue where Excel collapsed
  KPI tiles to one cell wide regardless of `layout="grid"`. Now arranges
  N tiles per row in both HTML (CSS grid) and Excel (column block math).

### PDF renderer rewrite

- Prefer **playwright (Chromium HTML to PDF)** for browser-grade fidelity.
  Works on Windows once `python -m playwright install chromium` has been
  run. Falls back to weasyprint (Linux/Mac), then to reportlab plain text
  as a last resort. All three paths render the same Dashboard input so
  callers don't care which backend won. Closes the showcase-audit pain
  point of "drab Courier-mono PDF on Windows."

### Tests

- 21 new tests in `tests/test_v030_features.py` covering all five gaps
  across the relevant renderers + IR validation + backwards compat.
- All 40 existing v0.2.0 tests still pass.

### Notes

- All additions are additive; v0.2.0 callers don't need to change.
- JSON Schema (`spec/schema/v1/dashboard.json`) extended for cover_page,
  roi_summary, table.cell_tones, and the new section layout literals.

---

## 0.2.0 — 2026-05-05

### New components for war-room rebuild
- `pipeline` — numbered horizontal stages with per-stage state
  (`ready` / `watching` / `blocked` / `shipped` / `neutral`). Funnel
  rendering for war-room, deploy pipelines, any ordered process.
- `link_grid` — grid of cards or row of chips. Chip mode supports an
  `ok` flag that renders OK / MISSING health badges. Card mode supports
  `kicker`, `detail`, and `tone`. Powers the war-room board rail and
  the bottom diag link list in one shape.
- `code_block` — pre-formatted text panel with optional caption /
  language. Powers war-room "dirty workspace" git-status tail.

### Renderer support
- HTML: full Palantir styling for all three new components, including
  responsive collapse on narrow viewports.
- Markdown: numbered stages with state glyphs, link list with health
  flags, fenced code block honouring `language`.
- Excel: pipeline stages render as bordered rows with tone-coloured
  values; link grid uses native hyperlinks; code block uses Consolas
  with wrap. Caption rows where present.
- PDF: piggybacks on HTML (weasyprint) or markdown (reportlab fallback)
  — both already cover the new components.

### Tests
- 4 new tests in `test_renderers.py`: HTML structural classes, markdown
  output shape, Excel smoke, JSON-IR roundtrip through `load()`.
- Total: 40 passing.

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
