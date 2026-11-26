"""F03 - Exercise 11.7 A-E: Analisis Kasus & Cycle Time (Milik Lintang).

Memenuhi seluruh butir soal 11.7:
- 11.7 A: Jumlah unique case pada seluruh log aktif.
- 11.7 B: Rata-rata cycle time seluruh case (hari), dengan denominator total case.
- 11.7 C: Jumlah case mengandung >= 1 O_Accepted (successful) + rata-rata full cycle time-nya.
- 11.7 D: Jumlah case mengandung >= 1 O_Refused (unsuccessful) + rata-rata full cycle time-nya.
- 11.7 E: Jumlah case dengan event paling akhir pada trace-nya adalah O_Cancelled + rata-rata full cycle time-nya.

Aturan Kritis:
1. C dan D TIDAK saling eksklusif (case yang memuat accepted dan refused boleh masuk keduanya).
2. Event berulang dalam 1 case (mis. O_Accepted 2x) tetap dihitung 1 case.
3. 11.7 E HANYA lolos jika event TERAKHIR dalam trace adalah O_Cancelled (bukan di tengah trace).
4. Cycle time dihitung dari TRACE LENGKAP masing-masing case dalam hari, BUKAN dari subset event.
5. Jika kelompok case kosong, case_count=0, case_ids=[], mean_cycle_days=None (N/A).
"""
from __future__ import annotations

from typing import Optional

import numpy as np
import pandas as pd

from core.cycle_time import case_durations_days

ACT_ACCEPTED = "O_Accepted"
ACT_REFUSED = "O_Refused"
ACT_CANCELLED = "O_Cancelled"

RULE_117_A = "Seluruh unique case pada log aktif."
RULE_117_B = "Rata-rata cycle time (max timestamp - min timestamp) seluruh case dalam hari."
RULE_117_C = "Case mengandung minimal satu event O_Accepted (successful). Cycle time dihitung dari trace lengkap."
RULE_117_D = "Case mengandung minimal satu event O_Refused (unsuccessful). Cycle time dihitung dari trace lengkap."
RULE_117_E = "Event terakhir pada urutan trace adalah O_Cancelled (canceled). Cycle time dihitung dari trace lengkap."


def exercise_117_a(df: pd.DataFrame, durations: Optional[pd.Series] = None) -> dict:
    """11.7 A: Jumlah unique case pada seluruh log aktif."""
    if df.empty or "case_id" not in df.columns:
        return {
            "exercise": "11.7 A",
            "title": "Exercise 11.7 A - Total Unique Cases",
            "case_count": 0,
            "case_ids": [],
            "filter_rule": RULE_117_A,
            "evidence": {},
            "metrics": {
                "numerator": 0,
                "denominator": 0,
                "mean_cycle_days": None,
            },
        }

    if durations is None:
        durations = case_durations_days(df)

    # Dapatkan daftar case ID unik dalam urutan kemunculan di log
    case_ids = [str(c) for c in df["case_id"].unique()]
    total_cases = len(case_ids)

    # Hitung jumlah event per case untuk evidence
    events_per_case = df.groupby("case_id", sort=False).size()

    evidence = {}
    for cid in case_ids:
        dur = float(durations.get(cid, 0.0))
        n_ev = int(events_per_case.get(cid, 0))
        evidence[cid] = {
            "reason": f"Case aktif ({n_ev} event, durasi {dur:.4f} hari)",
            "highlight_positions": [1],
            "duration_days": dur,
            "events_count": n_ev,
        }

    mean_days = float(durations.mean()) if len(durations) else None

    return {
        "exercise": "11.7 A",
        "title": "Exercise 11.7 A - Total Unique Cases",
        "case_count": total_cases,
        "case_ids": case_ids,
        "filter_rule": RULE_117_A,
        "evidence": evidence,
        "metrics": {
            "numerator": total_cases,
            "denominator": total_cases,
            "mean_cycle_days": mean_days,
        },
    }


def exercise_117_b(df: pd.DataFrame, durations: Optional[pd.Series] = None) -> dict:
    """11.7 B: Rata-rata cycle time seluruh case (hari)."""
    if df.empty or "case_id" not in df.columns:
        return {
            "exercise": "11.7 B",
            "title": "Exercise 11.7 B - Mean Cycle Time (All Cases)",
            "case_count": 0,
            "case_ids": [],
            "filter_rule": RULE_117_B,
            "evidence": {},
            "metrics": {
                "numerator": 0,
                "denominator": 0,
                "mean_cycle_days": None,
            },
        }

    if durations is None:
        durations = case_durations_days(df)

    case_ids = [str(c) for c in df["case_id"].unique()]
    total_cases = len(case_ids)
    mean_days = float(durations.mean()) if len(durations) else None

    events_per_case = df.groupby("case_id", sort=False).size()

    evidence = {}
    for cid in case_ids:
        dur = float(durations.get(cid, 0.0))
        n_ev = int(events_per_case.get(cid, 0))
        evidence[cid] = {
            "reason": f"Durasi trace lengkap: {dur:.4f} hari ({n_ev} event)",
            "highlight_positions": [1, n_ev] if n_ev > 1 else [1],
            "duration_days": dur,
            "events_count": n_ev,
        }

    return {
        "exercise": "11.7 B",
        "title": "Exercise 11.7 B - Mean Cycle Time (All Cases)",
        "case_count": total_cases,
        "case_ids": case_ids,
        "filter_rule": RULE_117_B,
        "evidence": evidence,
        "metrics": {
            "numerator": total_cases,
            "denominator": total_cases,
            "mean_cycle_days": mean_days,
        },
    }


def exercise_117_c(df: pd.DataFrame, durations: Optional[pd.Series] = None) -> dict:
    """11.7 C: Jumlah case mengandung >= 1 O_Accepted + rata-rata full cycle time-nya."""
    if df.empty or "case_id" not in df.columns:
        return {
            "exercise": "11.7 C",
            "title": "Exercise 11.7 C - Successful Cases (O_Accepted)",
            "case_count": 0,
            "case_ids": [],
            "filter_rule": RULE_117_C,
            "evidence": {},
            "metrics": {
                "numerator": 0,
                "denominator": 0,
                "percentage": None,
                "mean_cycle_days": None,
            },
        }

    if durations is None:
        durations = case_durations_days(df)

    total_cases = int(df["case_id"].nunique())
    accepted_df = df[df["activity"] == ACT_ACCEPTED]

    if accepted_df.empty:
        return {
            "exercise": "11.7 C",
            "title": "Exercise 11.7 C - Successful Cases (O_Accepted)",
            "case_count": 0,
            "case_ids": [],
            "filter_rule": RULE_117_C,
            "evidence": {},
            "metrics": {
                "numerator": 0,
                "denominator": total_cases,
                "percentage": 0.0 if total_cases else None,
                "mean_cycle_days": None,
            },
        }

    # Groupby case_id untuk mengumpulkan posisi bukti
    grouped = accepted_df.groupby("case_id", sort=False)
    case_ids = [str(c) for c in grouped.groups.keys()]

    evidence = {}
    subset_durations = []
    for cid in case_ids:
        c_events = accepted_df[accepted_df["case_id"] == cid]
        positions = [int(p) for p in c_events["position"].tolist()]
        count = len(positions)
        dur = float(durations.get(cid, 0.0))
        subset_durations.append(dur)
        evidence[cid] = {
            "reason": f"Mengandung {count}x O_Accepted (posisi: {', '.join(map(str, positions))}) | durasi trace: {dur:.4f} hari",
            "highlight_positions": positions,
            "duration_days": dur,
            "accepted_count": count,
        }

    mean_days = float(np.mean(subset_durations)) if len(subset_durations) else None
    n = len(case_ids)

    return {
        "exercise": "11.7 C",
        "title": "Exercise 11.7 C - Successful Cases (O_Accepted)",
        "case_count": n,
        "case_ids": case_ids,
        "filter_rule": RULE_117_C,
        "evidence": evidence,
        "metrics": {
            "numerator": n,
            "denominator": total_cases,
            "percentage": (n / total_cases * 100.0) if total_cases else None,
            "mean_cycle_days": mean_days,
        },
    }


def exercise_117_d(df: pd.DataFrame, durations: Optional[pd.Series] = None) -> dict:
    """11.7 D: Jumlah case mengandung >= 1 O_Refused + rata-rata full cycle time-nya."""
    if df.empty or "case_id" not in df.columns:
        return {
            "exercise": "11.7 D",
            "title": "Exercise 11.7 D - Unsuccessful Cases (O_Refused)",
            "case_count": 0,
            "case_ids": [],
            "filter_rule": RULE_117_D,
            "evidence": {},
            "metrics": {
                "numerator": 0,
                "denominator": 0,
                "percentage": None,
                "mean_cycle_days": None,
            },
        }

    if durations is None:
        durations = case_durations_days(df)

    total_cases = int(df["case_id"].nunique())
    refused_df = df[df["activity"] == ACT_REFUSED]

    if refused_df.empty:
        return {
            "exercise": "11.7 D",
            "title": "Exercise 11.7 D - Unsuccessful Cases (O_Refused)",
            "case_count": 0,
            "case_ids": [],
            "filter_rule": RULE_117_D,
            "evidence": {},
            "metrics": {
                "numerator": 0,
                "denominator": total_cases,
                "percentage": 0.0 if total_cases else None,
                "mean_cycle_days": None,
            },
        }

    grouped = refused_df.groupby("case_id", sort=False)
    case_ids = [str(c) for c in grouped.groups.keys()]

    evidence = {}
    subset_durations = []
    for cid in case_ids:
        c_events = refused_df[refused_df["case_id"] == cid]
        positions = [int(p) for p in c_events["position"].tolist()]
        count = len(positions)
        dur = float(durations.get(cid, 0.0))
        subset_durations.append(dur)
        evidence[cid] = {
            "reason": f"Mengandung {count}x O_Refused (posisi: {', '.join(map(str, positions))}) | durasi trace: {dur:.4f} hari",
            "highlight_positions": positions,
            "duration_days": dur,
            "refused_count": count,
        }

    mean_days = float(np.mean(subset_durations)) if len(subset_durations) else None
    n = len(case_ids)

    return {
        "exercise": "11.7 D",
        "title": "Exercise 11.7 D - Unsuccessful Cases (O_Refused)",
        "case_count": n,
        "case_ids": case_ids,
        "filter_rule": RULE_117_D,
        "evidence": evidence,
        "metrics": {
            "numerator": n,
            "denominator": total_cases,
            "percentage": (n / total_cases * 100.0) if total_cases else None,
            "mean_cycle_days": mean_days,
        },
    }


def exercise_117_e(df: pd.DataFrame, durations: Optional[pd.Series] = None) -> dict:
    """11.7 E: Jumlah case dengan event paling akhir pada trace-nya O_Cancelled + mean cycle time-nya."""
    if df.empty or "case_id" not in df.columns:
        return {
            "exercise": "11.7 E",
            "title": "Exercise 11.7 E - Canceled Cases (Endpoint O_Cancelled)",
            "case_count": 0,
            "case_ids": [],
            "filter_rule": RULE_117_E,
            "evidence": {},
            "metrics": {
                "numerator": 0,
                "denominator": 0,
                "percentage": None,
                "mean_cycle_days": None,
            },
        }

    if durations is None:
        durations = case_durations_days(df)

    total_cases = int(df["case_id"].nunique())

    # Cari event terakhir per case berdasarkan posisi tertinggi dalam trace
    last_idx = df.groupby("case_id", sort=False)["position"].idxmax()
    last_events = df.loc[last_idx]

    # Filter yang aktivitas terakhirnya tepat O_Cancelled
    canceled_last = last_events[last_events["activity"] == ACT_CANCELLED]

    if canceled_last.empty:
        return {
            "exercise": "11.7 E",
            "title": "Exercise 11.7 E - Canceled Cases (Endpoint O_Cancelled)",
            "case_count": 0,
            "case_ids": [],
            "filter_rule": RULE_117_E,
            "evidence": {},
            "metrics": {
                "numerator": 0,
                "denominator": total_cases,
                "percentage": 0.0 if total_cases else None,
                "mean_cycle_days": None,
            },
        }

    case_ids = [str(c) for c in canceled_last["case_id"].tolist()]
    evidence = {}
    subset_durations = []

    for row in canceled_last.itertuples(index=False):
        cid = str(row.case_id)
        last_pos = int(row.position)
        dur = float(durations.get(cid, 0.0))
        subset_durations.append(dur)
        evidence[cid] = {
            "reason": f"Event terakhir (urutan ke-{last_pos}) adalah O_Cancelled | durasi trace: {dur:.4f} hari",
            "highlight_positions": [last_pos],
            "duration_days": dur,
            "last_activity": ACT_CANCELLED,
            "last_position": last_pos,
        }

    mean_days = float(np.mean(subset_durations)) if len(subset_durations) else None
    n = len(case_ids)

    return {
        "exercise": "11.7 E",
        "title": "Exercise 11.7 E - Canceled Cases (Endpoint O_Cancelled)",
        "case_count": n,
        "case_ids": case_ids,
        "filter_rule": RULE_117_E,
        "evidence": evidence,
        "metrics": {
            "numerator": n,
            "denominator": total_cases,
            "percentage": (n / total_cases * 100.0) if total_cases else None,
            "mean_cycle_days": mean_days,
        },
    }


def exercise_117_all(df: pd.DataFrame) -> dict[str, dict]:
    """Jalankan kelima sub-analisis Exercise 11.7 (A, B, C, D, E) secara efisien."""
    durations = case_durations_days(df)
    return {
        "11.7 A": exercise_117_a(df, durations=durations),
        "11.7 B": exercise_117_b(df, durations=durations),
        "11.7 C": exercise_117_c(df, durations=durations),
        "11.7 D": exercise_117_d(df, durations=durations),
        "11.7 E": exercise_117_e(df, durations=durations),
    }
