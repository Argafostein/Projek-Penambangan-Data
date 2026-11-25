"""SEMENTARA - milik Lintang (cycle time, Exercise 11.7).

File ini hanya versi minimal agar Overview (F02) milik Ida bisa berjalan.
Setelah Lintang selesai, ganti isinya dengan versi Lintang selama dua fungsi
di bawah tetap ada dengan tanda tangan yang sama.

Cycle time satu case = timestamp event terakhir - timestamp event pertama (hari).
"""
from __future__ import annotations

from typing import Optional

import pandas as pd


def case_durations_days(df: pd.DataFrame) -> pd.Series:
    """Durasi tiap case dalam hari; index = case_id."""
    g = df.groupby("case_id", sort=False)["timestamp"]
    return ((g.max() - g.min()) / pd.Timedelta(days=1)).rename("duration_days")


def mean_cycle_days(df: pd.DataFrame) -> Optional[float]:
    s = case_durations_days(df)
    return float(s.mean()) if len(s) else None
