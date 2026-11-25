"""Test runner otomatis tanpa membuka GUI (menggunakan pytest).

Penggunaan:
    python run_tests.py            # jalankan seluruh unit test & GUI offscreen test
    python run_tests.py --unit     # jalankan hanya unit test core (tanpa GUI)
    python run_tests.py -q         # argumen tambahan diteruskan ke pytest
"""
from __future__ import annotations

import sys

import pytest


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    unit_only = False
    if "--unit" in args:
        args.remove("--unit")
        unit_only = True

    pytest_args = ["-v"]
    if unit_only:
        pytest_args.extend(["--ignore=tests/test_gui_smoke.py", "--ignore=tests/test_gui_1115_1118.py"])
    pytest_args.extend(args)

    return pytest.main(pytest_args)


if __name__ == "__main__":
    raise SystemExit(main())

