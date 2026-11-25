"""Pembuat log sintetis untuk pengujian (boleh dipakai Arga dan Lintang juga).

Contoh:
    log = make_log({
        "A": ["O_Cancelled", "W_Call", "O_Accepted"],
        "B": [("W_Assess Potential Fraud", "complete", "User_1")],
    })
Setiap event: string aktivitas, atau tuple (aktivitas, lifecycle, resource).
Timestamp naik 1 jam per event dalam satu case.
"""
from __future__ import annotations

import pandas as pd

from core.log_loader import LogData, build_log_data

BASE = pd.Timestamp("2016-01-01 08:00:00", tz="UTC")


def make_log(cases: dict) -> LogData:
    rows = []
    for cid, events in cases.items():
        for i, ev in enumerate(events):
            if isinstance(ev, str):
                ev = (ev, "complete", None)
            activity, lifecycle, resource = ev
            rows.append(
                {
                    "case:concept:name": cid,
                    "concept:name": activity,
                    "lifecycle:transition": lifecycle,
                    "org:resource": resource,
                    "time:timestamp": BASE + pd.Timedelta(hours=i),
                }
            )
    return build_log_data(pd.DataFrame(rows), "sintetis.xes")


def xes_text(cases: dict, with_timestamp: bool = True) -> str:
    out = ['<?xml version="1.0" encoding="UTF-8" ?>', '<log xes.version="1.0" xmlns="http://www.xes-standard.org/">']
    for cid, events in cases.items():
        out.append(f'<trace><string key="concept:name" value="{cid}"/>')
        for i, (activity, lifecycle, resource) in enumerate(events):
            out.append("<event>")
            out.append(f'<string key="concept:name" value="{activity}"/>')
            if lifecycle is not None:
                out.append(f'<string key="lifecycle:transition" value="{lifecycle}"/>')
            if resource is not None:
                out.append(f'<string key="org:resource" value="{resource}"/>')
            if with_timestamp:
                out.append(f'<date key="time:timestamp" value="2016-01-01T{8 + i:02d}:00:00.000+00:00"/>')
            out.append("</event>")
        out.append("</trace>")
    out.append("</log>")
    return "\n".join(out)
