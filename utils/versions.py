"""Informasi versi untuk menu About (reproduktibilitas eksperimen)."""
from __future__ import annotations

import platform
from importlib import metadata


def get_versions() -> dict:
    info = {"Python": platform.python_version()}
    for pkg in ("pm4py", "pandas", "numpy", "PySide6"):
        try:
            info[pkg] = metadata.version(pkg)
        except metadata.PackageNotFoundError:
            info[pkg] = "tidak terpasang"
    return info
