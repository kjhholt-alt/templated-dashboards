"""Vendored status-spec stub.

This is a minimal local stand-in for the sibling ``status-spec`` library.
When that library is published, replace this import with the real one;
the public surface (``read_status``) is identical.

A status file is a JSON document with at least these fields:

    {
        "project":      "operator-core",
        "tier":         "good" | "warn" | "bad",
        "last_update":  "2026-05-04T18:30:00Z",
        "summary":      "running, last heartbeat 30s ago",
        "metrics":      { "uptime_pct": 99.9, "queue_depth": 3 }
    }

``read_status(path_or_url)`` returns this as a Python dict.  This stub
only handles local file paths; the real lib will also handle HTTP(S).
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def read_status(path_or_url: str) -> dict[str, Any]:
    """Return the parsed status JSON, or an empty dict on missing file."""
    if path_or_url.startswith(("http://", "https://")):
        # Stub: refuse network. Caller should pass inline_status.
        return {
            "project": "",
            "tier": "neutral",
            "summary": f"network fetch not supported in stub: {path_or_url}",
        }

    p = Path(path_or_url)
    if not p.exists():
        return {
            "project": "",
            "tier": "neutral",
            "summary": f"status file not found: {p}",
        }
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception as e:  # pragma: no cover - I/O guard
        return {
            "project": "",
            "tier": "bad",
            "summary": f"failed to parse status file: {e}",
        }


__all__ = ["read_status"]
