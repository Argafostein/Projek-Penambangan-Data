"""F04/F05 - Pemeriksaan status lifecycle:transition berbasis representasi nyata XES.

Keputusan teknis:
1. Pada event log BPIC17 (dan standar XES lifecycle), status penyelesaian aktivitas
   dicatat pada atribut ``lifecycle:transition`` (kolom ``lifecycle`` di ``LogData.df``).
2. Hanya event dengan nilai ``lifecycle:transition`` == ``"complete"`` (case-insensitive,
   di-strip) yang dihitung sebagai penyelesaian aktivitas.
3. Status lain seperti ``schedule``, ``scheduled``, ``start``, ``suspend``, ``resume``,
   ``withdraw``, ``ate_abort``, ``pi_abort``, maupun nilai kosong/NaN tidak dihitung.
4. Jika atribut ``lifecycle:transition`` tidak ada atau kosong seluruhnya pada log,
   fungsi tidak mengasumsikan event selesai dan melaporkannya secara eksplisit.
"""
from __future__ import annotations

import pandas as pd

TARGET_ACTIVITY = "W_Assess Potential Fraud"
COMPLETE_STATUS = "complete"


def is_complete_series(df: pd.DataFrame) -> pd.Series:
    """Kembalikan Series boolean True hanya untuk event berstatus ``complete``."""
    if df.empty or "lifecycle" not in df.columns:
        return pd.Series(False, index=df.index, dtype=bool)
    return df["lifecycle"].map(
        lambda v: isinstance(v, str) and v.strip().lower() == COMPLETE_STATUS
    )


def is_identified_resource(series: pd.Series) -> pd.Series:
    """Kembalikan Series boolean True hanya untuk resource yang teridentifikasi (bukan null/kosong)."""
    if series.empty:
        return pd.Series(False, index=series.index, dtype=bool)
    return series.map(
        lambda v: (
            v is not None
            and not (isinstance(v, float) and pd.isna(v))
            and not pd.isna(v)
            and (not isinstance(v, str) or v.strip() != "")
        )
    )


def normalize_resource(value) -> str:
    """Normalisasi nilai resource teridentifikasi menjadi string bersih."""
    return str(value).strip()


def inspect_lifecycle(df: pd.DataFrame, activity: str = TARGET_ACTIVITY) -> dict:
    """Periksa representasi status lifecycle yang benar-benar ada pada log aktif."""
    has_col = "lifecycle" in df.columns
    has_lifecycle = bool(has_col and df["lifecycle"].notna().any())

    target_df = df[df["activity"] == activity] if not df.empty else df
    lifecycle_counts: dict[str, int] = {}
    if has_col and not target_df.empty:
        vc = target_df["lifecycle"].fillna("<kosong>").astype(str).value_counts()
        lifecycle_counts = {str(k): int(v) for k, v in vc.items()}

    complete_mask = is_complete_series(target_df)
    complete_count = int(complete_mask.sum()) if not target_df.empty else 0
    non_complete_count = int(len(target_df) - complete_count)

    if has_lifecycle:
        decision = (
            "Status selesai dikenali dari atribut XES lifecycle:transition == 'complete' "
            "(non-complete seperti schedule/start/abort dan nilai kosong diabaikan)."
        )
    else:
        decision = (
            "Atribut lifecycle:transition tidak ditemukan atau kosong seluruhnya pada log; "
            "tidak ada event yang dapat dipastikan berstatus complete."
        )

    return {
        "has_lifecycle": has_lifecycle,
        "source_attribute": "lifecycle:transition" if has_lifecycle else "tidak tersedia",
        "target_activity": activity,
        "target_total_events": int(len(target_df)),
        "target_complete_events": complete_count,
        "target_non_complete_events": non_complete_count,
        "lifecycle_counts": lifecycle_counts,
        "decision": decision,
    }


def filter_complete_target(df: pd.DataFrame, activity: str = TARGET_ACTIVITY) -> pd.DataFrame:
    """Ambil seluruh event untuk aktivitas target yang berstatus ``complete``."""
    if df.empty:
        return df.iloc[0:0].copy()
    mask = (df["activity"] == activity) & is_complete_series(df)
    return df.loc[mask].copy()

