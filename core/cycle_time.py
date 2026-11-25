"""F02 & F03 - Perhitungan Cycle Time Case (Milik Lintang).

Cycle time satu case = max(timestamp) - min(timestamp) pada seluruh trace kasus tersebut,
dinyatakan dalam satuan hari (float).

Aturan & Keputusan Teknis:
1. Cycle time dihitung berdasarkan keseluruhan trace kasus asli (full case trace),
   bukan dipotong oleh filter aktivitas (mis. O_Accepted / O_Refused).
2. Jika sebuah case hanya memiliki 1 event atau seluruh event memiliki timestamp sama,
   durasi case adalah 0.0 hari (sah).
3. Jika kumpulan case kosong (0 case), nilai rata-rata (mean) adalah None (ditampilkan
   sebagai N/A pada GUI), BUKAN 0 hari palsu.
4. Fungsi case_durations_days dan mean_cycle_days dipertahankan kompatibel dengan F02
   (Overview) milik Ida Bagus.
"""
from __future__ import annotations

from typing import Collection, Optional

import pandas as pd


def case_durations_days(df: pd.DataFrame) -> pd.Series:
    """Durasi tiap case dalam hari (float); index = case_id.

    Menggunakan seluruh trace case yang ada pada DataFrame.
    """
    if df.empty or "case_id" not in df.columns or "timestamp" not in df.columns:
        return pd.Series(dtype=float, name="duration_days")

    g = df.groupby("case_id", sort=False)["timestamp"]
    # Perbedaan waktu dalam detik dibagi 86400 (detik per hari)
    # Konsisten dan presisi untuk datetime dengan/tanpa timezone
    time_diff = (g.max() - g.min())
    if hasattr(time_diff, "dt"):
        days = time_diff.dt.total_seconds() / 86400.0
    else:
        days = time_diff.total_seconds() / 86400.0
    return days.rename("duration_days")


def mean_cycle_days(df: pd.DataFrame) -> Optional[float]:
    """Rerata cycle time seluruh case dalam DataFrame dalam hari.

    Mengembalikan None jika DataFrame kosong / tidak ada case.
    """
    s = case_durations_days(df)
    return float(s.mean()) if len(s) else None


def mean_cycle_days_for_cases(
    all_case_durations: pd.Series,
    target_case_ids: Collection[str],
) -> Optional[float]:
    """Hitung rata-rata cycle time untuk sekumpulan case_id tertentu
    dari Series durasi lengkap (agar trace tidak terpotong).

    Mengembalikan None jika target_case_ids kosong.
    """
    if not len(target_case_ids) or all_case_durations.empty:
        return None
    # Filter durasi hanya untuk case_id yang ditargetkan
    subset = all_case_durations[all_case_durations.index.isin(target_case_ids)]
    return float(subset.mean()) if len(subset) else None
