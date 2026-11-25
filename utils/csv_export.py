"""F07 - Ekspor hasil analisis ke CSV.

Format ``result`` (kontrak bersama seluruh modul analisis):
    exercise    str   kode unik, mis. "11.22"
    case_count  int
    case_ids    list[str]
    filter_rule str
    evidence    dict[case_id -> dict | list[dict]]
    metrics     dict[str -> angka/str/None]
"""
from __future__ import annotations

from typing import Any

import pandas as pd

ENCODING = "utf-8-sig"  # BOM agar Excel membaca UTF-8 dengan benar


def _cell(value: Any) -> Any:
    if isinstance(value, (list, tuple, set)):
        return "; ".join(str(v) for v in value)
    return value


def _flatten_evidence(ev: Any) -> list:
    """Ubah bukti satu case menjadi satu atau lebih baris (dict)."""
    if ev is None or ev == {} or ev == []:
        return [{}]
    if isinstance(ev, dict):
        return [{k: _cell(v) for k, v in ev.items()}]
    if isinstance(ev, (list, tuple)):
        rows: list = []
        for item in ev:
            rows.extend(_flatten_evidence(item) if isinstance(item, dict) else [{"evidence": _cell(item)}])
        return rows or [{}]
    return [{"evidence": _cell(ev)}]


def export_summary(results: dict, path: str) -> int:
    """Ringkasan jawaban: satu baris per metrik. Mengembalikan jumlah baris data."""
    rows = []
    for res in results.values():
        base = {
            "exercise": res.get("exercise", ""),
            "filter_rule": res.get("filter_rule", ""),
            "case_count": res.get("case_count", 0),
        }
        metrics = res.get("metrics") or {}
        if not metrics:
            rows.append({**base, "metric": "", "value": ""})
        for name, value in metrics.items():
            rows.append({**base, "metric": name, "value": "" if value is None else value})
    cols = ["exercise", "filter_rule", "case_count", "metric", "value"]
    pd.DataFrame(rows, columns=cols).to_csv(path, index=False, encoding=ENCODING)
    return len(rows)


def export_cases(result: dict, path: str) -> int:
    """Daftar case terpilih beserta buktinya. Hasil kosong tetap menghasilkan header."""
    evidence = result.get("evidence") or {}
    rows = []
    extra_cols: list = []
    for cid in result.get("case_ids", []):
        for part in _flatten_evidence(evidence.get(cid)):
            for key in part:
                if key not in extra_cols:
                    extra_cols.append(key)
            rows.append({"exercise": result.get("exercise", ""), "case_id": cid, **part})
    cols = ["exercise", "case_id"] + extra_cols
    pd.DataFrame(rows, columns=cols).to_csv(path, index=False, encoding=ENCODING)
    return len(rows)
