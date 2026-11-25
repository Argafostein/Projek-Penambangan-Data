"""F02 - Event Log Overview dan statistika dasar."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import pandas as pd

from core.cycle_time import case_durations_days
from core.log_loader import LogData


@dataclass(eq=False)
class Overview:
    source: LogData                 # log yang dianalisis (untuk mendeteksi hasil usang)
    total_cases: int
    total_events: int
    first_timestamp: pd.Timestamp
    last_timestamp: pd.Timestamp
    mean_cycle_days: Optional[float]
    activity_table: pd.DataFrame    # activity, events, cases
    case_table: pd.DataFrame        # case_id, start, end, events, duration_days


def compute_overview(log: LogData) -> Overview:
    df = log.df
    durations = case_durations_days(df)

    case_table = (
        df.groupby("case_id", sort=False)
        .agg(start=("timestamp", "min"), end=("timestamp", "max"), events=("position", "size"))
        .join(durations)
        .reset_index()
    )
    activity_table = (
        df.groupby("activity")
        .agg(events=("position", "size"), cases=("case_id", "nunique"))
        .sort_values("events", ascending=False)
        .reset_index()
    )
    return Overview(
        source=log,
        total_cases=int(df["case_id"].nunique()),
        total_events=int(len(df)),
        first_timestamp=df["timestamp"].min(),
        last_timestamp=df["timestamp"].max(),
        mean_cycle_days=float(durations.mean()) if len(durations) else None,
        activity_table=activity_table,
        case_table=case_table,
    )
