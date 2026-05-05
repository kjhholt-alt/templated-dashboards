"""Direct test runner — bypasses pytest if its output capture misbehaves.

Pytest discovery would still be the canonical way; this file is just an
escape hatch for environments where pytest output is mysteriously empty.
"""

from __future__ import annotations

import inspect
import sys
import tempfile
import traceback
from io import StringIO
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

from tests import (  # noqa: E402
    test_builder,
    test_cli,
    test_ir,
    test_renderers,
    test_status_stub,
)


class _CapsysShim:
    """Minimal capsys replacement: capture sys.stdout/sys.stderr."""

    def __init__(self):
        self._out = StringIO()
        self._err = StringIO()
        self._old = None

    def __enter__(self):
        self._old = (sys.stdout, sys.stderr)
        sys.stdout = self._out
        sys.stderr = self._err
        return self

    def __exit__(self, *exc):
        sys.stdout, sys.stderr = self._old

    def readouterr(self):
        out = self._out.getvalue()
        err = self._err.getvalue()
        self._out.truncate(0); self._out.seek(0)
        self._err.truncate(0); self._err.seek(0)

        class R:
            pass

        r = R()
        r.out = out
        r.err = err
        return r


def main() -> int:
    modules = [test_ir, test_renderers, test_builder, test_status_stub, test_cli]
    total = passed = failed = skipped = 0
    fails = []
    skips = []

    for m in modules:
        for name, fn in sorted(inspect.getmembers(m, inspect.isfunction)):
            if not name.startswith("test_"):
                continue
            total += 1
            sig = inspect.signature(fn)
            kwargs = {}
            tmp_dir_obj = None
            shim = None

            try:
                if "tmp_path" in sig.parameters:
                    tmp_dir_obj = tempfile.TemporaryDirectory()
                    kwargs["tmp_path"] = Path(tmp_dir_obj.name)
                if "capsys" in sig.parameters:
                    shim = _CapsysShim()
                    kwargs["capsys"] = shim

                if shim:
                    with shim:
                        fn(**kwargs)
                else:
                    fn(**kwargs)
                passed += 1
                print(f"PASS {m.__name__}.{name}")
            except SystemExit as e:
                # argparse uses SystemExit on bad args — some tests expect it
                # We treat unexpected SystemExit as fail; expected ones use pytest.raises
                failed += 1
                fails.append((m.__name__, name, f"SystemExit({e.code})"))
                print(f"FAIL {m.__name__}.{name}  SystemExit({e.code})")
            except Exception as e:
                # Skip-style outcomes from pytest.skip(...)
                if "Skipped" in type(e).__name__:
                    skipped += 1
                    skips.append((m.__name__, name, str(e)))
                    print(f"SKIP {m.__name__}.{name}  {e}")
                else:
                    failed += 1
                    fails.append((m.__name__, name, traceback.format_exc()))
                    print(f"FAIL {m.__name__}.{name}")
            finally:
                if tmp_dir_obj:
                    try:
                        tmp_dir_obj.cleanup()
                    except Exception:
                        pass

    print()
    print("=" * 60)
    print(f"{passed}/{total} passed, {failed} failed, {skipped} skipped")
    print("=" * 60)
    for mod, n, tb in fails:
        print(f"\n--- FAIL {mod}.{n} ---")
        print(tb)
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
