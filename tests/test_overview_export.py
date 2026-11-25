import pandas as pd

from core.overview import compute_overview
from utils.csv_export import export_cases, export_summary
from core.exercise_1122 import exercise_1122
from helpers import make_log


def test_overview_counts_and_mean_cycle():
    log = make_log({"A": ["X", "Y", "Z"], "B": ["X", "Y"], "C": ["X"]})
    ov = compute_overview(log)
    assert (ov.total_cases, ov.total_events) == (3, 6)
    # durasi: 2 jam, 1 jam, 0 -> rata-rata 1 jam = 1/24 hari
    assert abs(ov.mean_cycle_days - (1 / 24)) < 1e-9
    assert ov.activity_table.iloc[0]["activity"] == "X"
    assert ov.activity_table.iloc[0]["cases"] == 3
    assert len(ov.case_table) == 3


def test_export_summary_and_cases(tmp_path):
    log = make_log({"A": ["O_Cancelled", "O_Accepted"], "B": ["X"]})
    res = exercise_1122(log.df)
    p1, p2 = tmp_path / "s.csv", tmp_path / "c.csv"
    export_summary({"11.22": res}, str(p1))
    export_cases(res, str(p2))
    s = pd.read_csv(p1, encoding="utf-8-sig")
    assert set(s["metric"]) >= {"numerator", "denominator", "percentage"}
    c = pd.read_csv(p2, encoding="utf-8-sig")
    assert list(c["case_id"]) == ["A"] and "reason" in c.columns


def test_export_empty_result_has_header(tmp_path):
    res = exercise_1122(make_log({"A": ["X"]}).df)
    p = tmp_path / "e.csv"
    assert export_cases(res, str(p)) == 0
    assert list(pd.read_csv(p, encoding="utf-8-sig").columns) == ["exercise", "case_id"]
