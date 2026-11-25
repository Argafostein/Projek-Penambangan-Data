"""F05 - Exercise 11.18: W_Assess Potential Fraud complete >= 2 kali oleh resource yang sama.

Aturan:
- Dimulai dari event ``W_Assess Potential Fraud`` berstatus ``lifecycle:transition == 'complete'``.
- Case lolos jika ada minimal 2 event ``complete`` pada case tersebut yang memiliki
  ``org:resource`` yang SAMA dan TERIDENTIFIKASI (tidak null, tidak kosong/spasi).
- Dua event ``complete`` dengan resource kosong/null TIDAK dianggap sama dan tidak meloloskan case.
- Dua event ``complete`` dengan resource berbeda lolos 11.15 tetapi TIDAK otomatis lolos 11.18.
- Satu case tetap dihitung sekali meskipun terdapat lebih dari satu resource yang masing-masing
  menyelesaikan >= 2 kali.
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
    "Case dipilih jika aktivitas 'W_Assess Potential Fraud' berstatus "
    "lifecycle:transition == 'complete' minimal 2 kali dalam case yang sama oleh "
    "org:resource yang SAMA dan teridentifikasi (nilai kosong/null tidak dianggap sama). "
    "Dihitung per unique case."
)


def exercise_1118(
    df: pd.DataFrame,
    activity: str = TARGET_ACTIVITY,
    min_complete: int = 2,
) -> dict:
    """Jalankan analisis Exercise 11.18 pada DataFrame log aktif."""
    total_cases = int(df["case_id"].nunique()) if not df.empty else 0
    lifecycle_info = inspect_lifecycle(df, activity=activity)
    completed = filter_complete_target(df, activity=activity)

    cases_passing_1115 = 0
    total_complete_with_null_resource = 0

    case_ids: list[str] = []
    evidence: dict[str, dict] = {}

    if not completed.empty:
        cases_passing_1115 = int(
            (completed.groupby("case_id").size() >= min_complete).sum()
        )
        identified_mask = is_identified_resource(completed["resource"])
        total_complete_with_null_resource = int((~identified_mask).sum())

        valid = completed.loc[identified_mask].copy()
        if not valid.empty:
            valid["_res_clean"] = valid["resource"].map(normalize_resource)
            valid = valid.sort_values(["case_id", "position"])

            for cid, case_group in valid.groupby("case_id", sort=True):
                qualifying: list[tuple[str, pd.DataFrame]] = []
                for res_id, res_group in case_group.groupby("_res_clean", sort=True):
                    if len(res_group) >= min_complete:
                        qualifying.append((str(res_id), res_group))

                if not qualifying:
                    continue

                # Urutkan resource berdasarkan jumlah complete terbanyak, lalu nama resource
                qualifying.sort(key=lambda item: (-len(item[1]), item[0]))
                primary_res, primary_group = qualifying[0]

                all_ev = pd.concat([g for _, g in qualifying]).sort_values("position")
                positions = [int(p) for p in all_ev["position"].tolist()]
                timestamps = all_ev["timestamp"].tolist()
                res_names = [r for r, _ in qualifying]
                res_summary = "; ".join(f"{r} ({len(g)}x)" for r, g in qualifying)

                cid_str = str(cid)
                case_ids.append(cid_str)
                evidence[cid_str] = {
                    "primary_resource": primary_res,
                    "max_complete_by_same_resource": int(len(primary_group)),
                    "qualifying_resources": res_names,
                    "resource_summary": res_summary,
                    "positions": positions,
                    "timestamps": timestamps,
                    "highlight_positions": positions,
                    "reason": (
                        f"{activity} complete >= {min_complete}x oleh resource sama: {res_summary}"
                    ),
                }

    n = len(case_ids)
    return {
        "exercise": "11.18",
        "title": "W_Assess Potential Fraud complete >= 2 kali oleh resource sama",
        "case_count": n,
        "case_ids": case_ids,
        "filter_rule": FILTER_RULE,
        "evidence": evidence,
        "lifecycle_info": lifecycle_info,
        "metrics": {
            "numerator": n,
            "denominator": total_cases,
            "percentage": (n / total_cases * 100.0) if total_cases else None,
            "cases_passing_1115": cases_passing_1115,
            "cases_excluded_diff_or_null_resource": max(0, cases_passing_1115 - n),
            "total_complete_with_null_resource": total_complete_with_null_resource,
            "lifecycle_source": lifecycle_info["source_attribute"],
        },
    }

