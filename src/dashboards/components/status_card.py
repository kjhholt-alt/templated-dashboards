"""status_card component helpers.

The component reads a status file (compatible with ``status-spec``) and
exposes a normalised view for renderers. Uses the vendored stub if the
real package isn't installed.
"""

from __future__ import annotations

from typing import Optional

from ..ir import StatusCard

try:
    from status_spec import read_status as _read_status  # type: ignore
except Exception:  # pragma: no cover - exercised when sibling lib absent
    from .._status_stub import read_status as _read_status


def resolve(card: StatusCard) -> dict:
    """Return a status dict for the card. Inline takes precedence over URL.

    The resolved dict has at least ``project``, ``tier`` (good/warn/bad),
    ``last_update``, and ``summary`` keys.
    """
    if card.inline_status is not None:
        raw = dict(card.inline_status)
    elif card.status_url:
        raw = _read_status(card.status_url)
    else:
        raw = {}

    return _normalise(card.project, raw)


def _normalise(project: str, raw: dict) -> dict:
    tier = (raw.get("tier") or raw.get("status") or "neutral").lower()
    if tier in ("green", "ok", "healthy"):
        tier = "good"
    elif tier in ("yellow", "amber", "degraded"):
        tier = "warn"
    elif tier in ("red", "down", "broken", "error"):
        tier = "bad"
    elif tier not in ("good", "warn", "bad", "neutral"):
        tier = "neutral"

    return {
        "project": project,
        "tier": tier,
        "last_update": raw.get("last_update") or raw.get("updated_at") or "",
        "summary": raw.get("summary") or raw.get("note") or "",
        "metrics": raw.get("metrics") or {},
        "raw": raw,
    }


__all__ = ["resolve"]
