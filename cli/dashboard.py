"""Top-level CLI entry point. Allows ``python cli/dashboard.py ...``.

The packaged entrypoint is ``dashboards.cli:main`` (registered in
pyproject.toml as the ``dashboard`` console script).
"""

from __future__ import annotations

import sys
from pathlib import Path

# Make `src/` importable when running this file directly.
_HERE = Path(__file__).resolve().parent
_SRC = _HERE.parent / "src"
if _SRC.exists():
    sys.path.insert(0, str(_SRC))

from dashboards.cli import main  # noqa: E402

if __name__ == "__main__":
    raise SystemExit(main())
