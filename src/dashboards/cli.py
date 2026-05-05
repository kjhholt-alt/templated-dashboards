"""CLI: ``dashboard render <ir.json> --format html [--out path]``.

Thin argparse wrapper around ``dashboards.render``.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from . import load, render


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="dashboard")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_render = sub.add_parser("render", help="render an IR file")
    p_render.add_argument("ir", type=Path, help="path to IR JSON")
    p_render.add_argument(
        "--format", "-f", required=True,
        choices=["html", "markdown", "md", "excel", "xlsx", "pdf"],
    )
    p_render.add_argument("--out", "-o", type=Path, default=None)

    p_validate = sub.add_parser("validate", help="validate an IR file")
    p_validate.add_argument("ir", type=Path)

    args = parser.parse_args(argv)

    if args.cmd == "render":
        dash = load(args.ir)
        result = render(dash, args.format, out=args.out)
        if isinstance(result, str):
            sys.stdout.write(result)
        else:
            print(str(result))
        return 0

    if args.cmd == "validate":
        load(args.ir)
        print(f"OK: {args.ir} validates against IR v1")
        return 0

    return 2


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
