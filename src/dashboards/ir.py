"""IR (Intermediate Representation) types and JSON validation.

The IR is the contract between callers and renderers.  Pydantic gives
us typed in-process construction; the JSON Schema in
`spec/schema/v1/dashboard.json` gives us cross-language validation.
This module wires both together.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Annotated, Any, List, Literal, Optional, Union

from pydantic import BaseModel, ConfigDict, Field

# ---------------------------------------------------------------------------
# Primitives
# ---------------------------------------------------------------------------

Tone = Literal["good", "warn", "bad", "neutral"]
Theme = Literal["palantir", "light"]
Layout = Literal["stack", "grid"]
ChartKind = Literal["bar", "line", "sparkline"]


class _Strict(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)


# ---------------------------------------------------------------------------
# Components
# ---------------------------------------------------------------------------


class StatusCard(_Strict):
    type: Literal["status_card"] = "status_card"
    project: str
    status_url: Optional[str] = None
    inline_status: Optional[dict] = None


class KPITile(_Strict):
    type: Literal["kpi_tile"] = "kpi_tile"
    label: str
    value: Union[str, float, int]
    delta: Optional[str] = None
    tone: Tone = "neutral"


class Table(_Strict):
    type: Literal["table"] = "table"
    headers: List[str]
    rows: List[List[Union[str, float, int, None]]]
    caption: Optional[str] = None


class TimelineEvent(_Strict):
    when: str
    title: str
    detail: Optional[str] = None
    tone: Tone = "neutral"


class Timeline(_Strict):
    type: Literal["timeline"] = "timeline"
    events: List[TimelineEvent]


class Callout(_Strict):
    type: Literal["callout"] = "callout"
    text: str
    tone: Tone = "neutral"
    icon: Optional[str] = None


class ChartSeries(_Strict):
    label: str
    points: List[float]


class Chart(_Strict):
    type: Literal["chart"] = "chart"
    kind: ChartKind
    series: List[ChartSeries]
    caption: Optional[str] = None


PipelineState = Literal["ready", "watching", "blocked", "shipped", "neutral"]


class PipelineStage(_Strict):
    name: str
    value: Union[str, float, int]
    state: PipelineState = "neutral"
    detail: Optional[str] = None


class Pipeline(_Strict):
    """Numbered horizontal stages with state per stage.

    Useful for funnels (Lead -> Approve -> Visit -> ... -> Close),
    deploy pipelines, or any ordered process.
    """

    type: Literal["pipeline"] = "pipeline"
    stages: List[PipelineStage]
    caption: Optional[str] = None


class LinkItem(_Strict):
    label: str
    href: str
    kicker: Optional[str] = None
    detail: Optional[str] = None
    tone: Tone = "neutral"
    ok: Optional[bool] = None


class LinkGrid(_Strict):
    """A grid or chip-row of links, optionally with health flags.

    ``style="card"`` renders large card tiles (kicker + label + detail).
    ``style="chip"`` renders compact pill chips with optional ok/missing
    badges driven by ``ok``.
    """

    type: Literal["link_grid"] = "link_grid"
    items: List[LinkItem]
    style: Literal["card", "chip"] = "card"
    caption: Optional[str] = None


class CodeBlock(_Strict):
    """Pre-formatted text block. Used for git status, log tails, etc."""

    type: Literal["code_block"] = "code_block"
    text: str
    language: Optional[str] = None
    caption: Optional[str] = None


Component = Annotated[
    Union[StatusCard, KPITile, Table, Timeline, Callout, Chart, Pipeline, LinkGrid, CodeBlock],
    Field(discriminator="type"),
]


class Section(_Strict):
    title: str
    subtitle: Optional[str] = None
    layout: Layout = "stack"
    components: List[Component]


class Dashboard(_Strict):
    """The Pydantic-validated IR document.

    Use the fluent ``builder.Dashboard`` for ergonomic construction;
    this class is the schema-true root.
    """

    version: Literal["1"] = "1"
    title: str
    subtitle: Optional[str] = None
    theme: Theme = "palantir"
    sections: List[Section]
    footer: Optional[str] = None


# ---------------------------------------------------------------------------
# Schema loading + validation
# ---------------------------------------------------------------------------


def _schema_path() -> Path:
    here = Path(__file__).resolve().parent
    candidates = [
        here.parent.parent / "spec" / "schema" / "v1" / "dashboard.json",
        here / "schema" / "v1" / "dashboard.json",
    ]
    for c in candidates:
        if c.exists():
            return c
    raise FileNotFoundError(
        "dashboard.json schema not found; expected at spec/schema/v1/"
    )


def schema() -> dict:
    """Return the JSON Schema as a dict (cached on first call)."""
    if not hasattr(schema, "_cached"):
        schema._cached = json.loads(_schema_path().read_text(encoding="utf-8"))
    return schema._cached


def validate(data: dict) -> None:
    """Validate raw JSON-ish dict against the JSON Schema. Raises on failure."""
    try:
        from jsonschema import Draft202012Validator
    except ImportError as e:  # pragma: no cover
        raise RuntimeError("jsonschema is required for IR validation") from e

    Draft202012Validator(schema()).validate(data)


def load(data: Union[dict, str, bytes, Path]) -> Dashboard:
    """Load a dashboard IR from a dict, JSON string, JSON bytes, or path.

    Validates against both the JSON Schema and the Pydantic model.
    """
    if isinstance(data, Path):
        raw = json.loads(data.read_text(encoding="utf-8"))
    elif isinstance(data, (str, bytes)):
        # Heuristic: treat strings ending in .json as paths if they exist;
        # otherwise treat as JSON content.
        if isinstance(data, str) and data.strip().startswith("{"):
            raw = json.loads(data)
        elif isinstance(data, bytes):
            raw = json.loads(data.decode("utf-8"))
        else:
            p = Path(data)
            if p.exists():
                raw = json.loads(p.read_text(encoding="utf-8"))
            else:
                raw = json.loads(data)
    elif isinstance(data, dict):
        raw = data
    else:
        raise TypeError(f"unsupported input type: {type(data).__name__}")

    validate(raw)
    return Dashboard.model_validate(raw)


def dump(dashboard: Dashboard, *, indent: int = 2) -> str:
    """Serialize a Dashboard to a JSON string."""
    return json.dumps(
        dashboard.model_dump(exclude_none=True),
        indent=indent,
        ensure_ascii=True,
    )
