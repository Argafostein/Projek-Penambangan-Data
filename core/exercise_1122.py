"""F06 - Exercise 11.22: adakah O_Cancelled yang kemudian diikuti O_Accepted?

Aturan (eventually follows): sebuah case lolos jika ada pasangan posisi i < j
dengan event i = O_Cancelled dan event j = O_Accepted. Keduanya TIDAK harus
bertetangga. Ini berbeda dengan 11.7 E yang hanya melihat event TERAKHIR.

Cara kerja: ambil posisi O_Cancelled paling awal di setiap case, lalu cari
O_Accepted pertama yang posisinya lebih besar. Jika ada, pasangan itulah bukti
(witness) bahwa urutan terpenuhi.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

CANCELLED = "O_Cancelled"
ACCEPTED = "O_Accepted"

FILTER_RULE = (
    "Case dipilih jika ada event O_Cancelled pada posisi i dan event O_Accepted "
    "pada posisi j dengan i < j (eventually follows; tidak harus bertetangga). "
    "Persentase = case lolos / seluruh case pada log aktif x 100%."
)


def exercise_1122(df: pd.DataFrame) -> dict:
    total_cases = int(df["case_id"].nunique())
    cancelled = df[df["activity"] == CANCELLED]
    accepted = df[df["activity"] == ACCEPTED]
    cases_with_both = int(
        len(np.intersect1d(cancelled["case_id"].unique(), accepted["case_id"].unique()))
    )

    witnesses = pd.DataFrame()
    if not cancelled.empty and not accepted.empty:
        first_cancel = (
            cancelled.loc[
                cancelled.groupby("case_id")["position"].idxmin(),
                ["case_id", "position", "timestamp"],
            ]
            .set_index("case_id")
            .rename(columns={"position": "cancel_pos", "timestamp": "cancel_ts"})
        )
        pairs = (
            accepted[["case_id", "position", "timestamp"]]
            .join(first_cancel, on="case_id", how="inner")
            .reset_index(drop=True)
        )
        pairs = pairs[pairs["position"] > pairs["cancel_pos"]]
        if not pairs.empty:
            witnesses = pairs.loc[pairs.groupby("case_id")["position"].idxmin()]
            witnesses = witnesses.sort_values("case_id")

    case_ids: list = []
    evidence: dict = {}
    for row in witnesses.itertuples(index=False):
        cid = row.case_id
        case_ids.append(cid)
        evidence[cid] = {
            "cancelled_position": int(row.cancel_pos),
            "cancelled_timestamp": row.cancel_ts,
            "accepted_position": int(row.position),
            "accepted_timestamp": row.timestamp,
            "highlight_positions": [int(row.cancel_pos), int(row.position)],
            "reason": (
                f"O_Cancelled (urutan ke-{int(row.cancel_pos)}) terjadi sebelum "
                f"O_Accepted (urutan ke-{int(row.position)})"
            ),
        }

    n = len(case_ids)
    return {
        "exercise": "11.22",
        "title": "O_Cancelled kemudian O_Accepted",
        "case_count": n,
        "case_ids": case_ids,
        "filter_rule": FILTER_RULE,
        "evidence": evidence,
        "metrics": {
            "numerator": n,
            "denominator": total_cases,
            "percentage": (n / total_cases * 100.0) if total_cases else None,
            "cases_with_both_activities": cases_with_both,
        },
    }
