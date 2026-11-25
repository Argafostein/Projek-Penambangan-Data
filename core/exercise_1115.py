"""F04 - Exercise 11.15: W_Assess Potential Fraud selesai (complete) minimal 2 kali.

Aturan:
- Aktivitas target: ``W_Assess Potential Fraud`` (``concept:name``).
- Status penyelesaian: ``lifecycle:transition == 'complete'`` (case-insensitive).
- Event ``schedule``, ``scheduled``, ``start``, ``abort``, ``suspend``, ``resume``,
  atau kosong tidak dihitung sebagai penyelesaian.
- Dihitung jumlah unique case (satu case dengan >= 2 complete tetap dihitung sekali).
"""
from __future__ import annotations

import pandas as pd

from core.lifecycle import (
    TARGET_ACTIVITY,
    filter_complete_target,
    inspect_lifecycle,
    is_identified_resource,
    normalize_resource,
)

FILTER_RULE = (
    "Case dipilih jika aktivitas 'W_Assess Potential Fraud' memiliki status "
    "lifecycle:transition == 'complete' minimal 2 kali dalam case yang sama. "
    "Status non-complete (schedule, start, abort, dll.) tidak dihitung. "
    "Dihitung per unique case."
)


def exercise_1115(
    df: pd.DataFrame,
    activity: str = TARGET_ACTIVITY,
    min_complete: int = 2,
) -> dict:
    """Jalankan analisis Exercise 11.15 pada DataFrame log aktif."""
    total_cases = int(df["case_id"].nunique()) if not df.empty else 0
    lifecycle_info = inspect_lifecycle(df, activity=activity)
    completed = filter_complete_target(df, activity=activity)

    cases_with_any_complete = int(completed["case_id"].nunique()) if not completed.empty else 0

    case_ids: list[str] = []
    evidence: dict[str, dict] = {}

    if not completed.empty:
        completed = completed.sort_values(["case_id", "position"])
        for cid, group in completed.groupby("case_id", sort=True):
            count = int(len(group))
            if count < min_complete:
                continue
            cid_str = str(cid)
            positions = [int(p) for p in group["position"].tolist()]
            timestamps = group["timestamp"].tolist()
            res_mask = is_identified_resource(group["resource"])
            resources = [
                normalize_resource(r) if ok else "<kosong>"
                for r, ok in zip(group["resource"].tolist(), res_mask.tolist())
            ]
            case_ids.append(cid_str)
            evidence[cid_str] = {
                "complete_count": count,
                "first_complete_timestamp": timestamps[0],
                "last_complete_timestamp": timestamps[-1],
                "positions": positions,
                "timestamps": timestamps,
                "resources": resources,
                "highlight_positions": positions,
                "reason": (
                    f"{activity} berstatus complete {count} kali "
                    f"(posisi {', '.join(map(str, positions))})"
                ),
            }

    n = len(case_ids)
    return {
        "exercise": "11.15",
        "title": "W_Assess Potential Fraud complete >= 2 kali",
        "case_count": n,
        "case_ids": case_ids,
        "filter_rule": FILTER_RULE,
        "evidence": evidence,
        "lifecycle_info": lifecycle_info,
        "metrics": {
            "numerator": n,
            "denominator": total_cases,
            "percentage": (n / total_cases * 100.0) if total_cases else None,
            "cases_with_any_complete": cases_with_any_complete,
            "total_target_events": lifecycle_info["target_total_events"],
            "total_complete_events": lifecycle_info["target_complete_events"],
            "lifecycle_source": lifecycle_info["source_attribute"],
        },
    }

