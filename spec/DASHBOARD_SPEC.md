# Dashboard IR Spec — v1

The Intermediate Representation (IR) is the single source of truth.
A dashboard is a JSON document; renderers consume it and emit
HTML / Markdown / Excel / PDF.

Schema file: [`schema/v1/dashboard.json`](schema/v1/dashboard.json).

## Top level

| Field      | Type                | Required | Description |
|------------|---------------------|----------|-------------|
| `version`  | `"1"`               | yes      | Schema version. Currently `"1"`. |
| `title`    | string              | yes      | Document title. |
| `subtitle` | string              | no       | Short subhead. Often a date. |
| `theme`    | `"palantir"`/`"light"` | no    | Default `"palantir"`. CSS only. |
| `sections` | `Section[]`         | yes      | Ordered, at least one. |
| `footer`   | string              | no       | Inline-rendered, escaped. |

## Section

| Field        | Type          | Required | Description |
|--------------|---------------|----------|-------------|
| `title`      | string        | yes      | Section heading. |
| `subtitle`   | string        | no       | Short subhead. |
| `components` | `Component[]` | yes      | At least one component. |
| `layout`     | `"stack"`/`"grid"` | no  | Default `"stack"`. HTML hint only. |

## Components

Every component is a tagged-union `{type: <kind>, ...}`. The renderer
dispatches on `type`. Adding a component type means updating all four
renderers (or explicitly declaring an "html-only" renderer that
renders a callout in the others).

### `status_card`

Reads a status file (compatible with the sibling `status-spec` lib) and
renders a project health card.

| Field        | Type   | Required | Description |
|--------------|--------|----------|-------------|
| `project`    | string | yes      | Display name. |
| `status_url` | string | no       | Path/URL to the status JSON. If absent, `inline_status` must be set. |
| `inline_status` | object | no    | Embedded status object. Used in tests / when caller pre-resolved. |

### `kpi_tile`

A single big-number KPI.

| Field   | Type            | Required | Description |
|---------|-----------------|----------|-------------|
| `label` | string          | yes      | Short label. |
| `value` | string / number | yes      | Big number. |
| `delta` | string          | no       | e.g. `"+12"`, `"-3%"`. |
| `tone`  | `"good"`/`"warn"`/`"bad"`/`"neutral"` | no | Default `"neutral"`. |

### `table`

| Field     | Type           | Required | Description |
|-----------|----------------|----------|-------------|
| `headers` | string[]       | yes      | Column headers. |
| `rows`    | (string/number/null)[][] | yes | Each row matches `headers` length. |
| `caption` | string         | no       | Caption above the table. |

### `timeline`

A sequence of dated events.

| Field    | Type            | Required | Description |
|----------|-----------------|----------|-------------|
| `events` | `TimelineEvent[]` | yes    | Ordered. |

`TimelineEvent`:

| Field    | Type   | Required | Description |
|----------|--------|----------|-------------|
| `when`   | string | yes      | Free-form date/time string. |
| `title`  | string | yes      | Headline. |
| `detail` | string | no       | Supporting text. |
| `tone`   | `"good"`/`"warn"`/`"bad"`/`"neutral"` | no | |

### `callout`

A highlighted note. Used for blockers, important context, html-only
fallbacks.

| Field   | Type   | Required | Description |
|---------|--------|----------|-------------|
| `text`  | string | yes      | Body. Plain text, auto-escaped. |
| `tone`  | `"good"`/`"warn"`/`"bad"`/`"neutral"` | no | Default `"neutral"`. |
| `icon`  | string | no       | Single-char hint (e.g. `!`). |

### `chart` (html-only in v1)

| Field    | Type    | Required | Description |
|----------|---------|----------|-------------|
| `kind`   | `"bar"`/`"line"`/`"sparkline"` | yes | |
| `series` | `{label: str, points: number[]}[]` | yes | |
| `caption`| string  | no       | |

Renderers other than HTML emit a `callout` saying "chart omitted in
this format". This is documented degradation, not a bug.

### `pipeline`

Numbered horizontal stages with state per stage. Useful for funnels,
deploy pipelines, and any ordered process.

| Field      | Type              | Required | Description |
|------------|-------------------|----------|-------------|
| `stages`   | `PipelineStage[]` | yes      | At least one. |
| `caption`  | string            | no       | |

`PipelineStage`:

| Field    | Type            | Required | Description |
|----------|-----------------|----------|-------------|
| `name`   | string          | yes      | Stage label. |
| `value`  | string / number | yes      | Stage count or display string. |
| `state`  | `"ready"`/`"watching"`/`"blocked"`/`"shipped"`/`"neutral"` | no | Default `"neutral"`. |
| `detail` | string          | no       | Optional hint. |

### `link_grid`

A grid (cards) or row (chips) of links, optionally with health flags.

| Field     | Type         | Required | Description |
|-----------|--------------|----------|-------------|
| `items`   | `LinkItem[]` | yes      | At least one. |
| `style`   | `"card"`/`"chip"` | no  | Default `"card"`. |
| `caption` | string       | no       | |

`LinkItem`:

| Field    | Type   | Required | Description |
|----------|--------|----------|-------------|
| `label`  | string | yes      | Display text. |
| `href`   | string | yes      | URL (relative ok). |
| `kicker` | string | no       | Small uppercase prefix. |
| `detail` | string | no       | Sub-label / description. |
| `tone`   | `"good"`/`"warn"`/`"bad"`/`"neutral"` | no | Card accent. |
| `ok`     | boolean| no       | When set, chip style adds OK / MISSING badge. |

### `code_block`

Pre-formatted text. Used for git status tails, log excerpts, etc.

| Field      | Type   | Required | Description |
|------------|--------|----------|-------------|
| `text`     | string | yes      | Body. Auto-escaped. |
| `language` | string | no       | Hint for markdown fences. |
| `caption`  | string | no       | |

## Rules

1. Renderers MUST be pure functions of IR.
2. Validation runs in `dashboards.ir.load()` and is the only place
   schema enforcement lives.
3. All user content is auto-escaped. No raw HTML passthrough.
4. Themes are CSS strings keyed by name; the IR carries only the name.
5. Adding fields = `version: "1"` stays valid (additive). Breaking
   changes bump to `"2"`.

## Versioning

The library follows semver. The IR version is independent — when the
IR breaks, we ship adapters in `dashboards.ir.migrate`.
