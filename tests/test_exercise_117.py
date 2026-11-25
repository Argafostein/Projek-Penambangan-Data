"""Unit test untuk Exercise 11.7 A-E dan perhitungan cycle time (Milik Lintang)."""
from __future__ import annotations

from pathlib import Path

import pytest

from core.cycle_time import case_durations_days, mean_cycle_days
from core.exercise_117 import (
    exercise_117_a,
    exercise_117_all,
    exercise_117_b,
    exercise_117_c,
    exercise_117_d,
    exercise_117_e,
)
from core.log_loader import load_log
from tests.helpers import make_log

SAMPLE_XES = Path(__file__).resolve().parent.parent / "sample_data" / "sample_log.xes"


def test_repeated_accepted_counted_once_117_c():
    """Case dengan O_Accepted dua kali tetap dihitung satu kali oleh 11.7 C."""
    log = make_log({
        "C1": ["O_Create Offer", "O_Accepted", "W_Call", "O_Accepted"],
        "C2": ["O_Create Offer"],
    })
    res_c = exercise_117_c(log.df)
    assert res_c["case_count"] == 1
    assert res_c["case_ids"] == ["C1"]
    ev = res_c["evidence"]["C1"]
    assert ev["accepted_count"] == 2
    assert ev["highlight_positions"] == [2, 4]


def test_accepted_and_refused_overlap_c_and_d():
    """Case dengan O_Accepted dan O_Refused boleh masuk kedua filter 11.7 C dan 11.7 D."""
    log = make_log({
        "C_both": ["O_Accepted", "O_Refused"],
        "C_acc_only": ["O_Accepted"],
        "C_ref_only": ["O_Refused"],
    })
    res_c = exercise_117_c(log.df)
    res_d = exercise_117_d(log.df)

    assert set(res_c["case_ids"]) == {"C_both", "C_acc_only"}
    assert set(res_d["case_ids"]) == {"C_both", "C_ref_only"}
    assert "C_both" in res_c["case_ids"] and "C_both" in res_d["case_ids"]


def test_cancelled_in_middle_not_endpoint_117_e():
    """Case dengan O_Cancelled di tengah dan event lain setelahnya TIDAK lolos 11.7 E."""
    log = make_log({
        "C_mid": ["O_Cancelled", "W_Call after offers"],
        "C_last": ["W_Call after offers", "O_Cancelled"],
    })
    res_e = exercise_117_e(log.df)
    assert res_e["case_ids"] == ["C_last"]
    assert "C_mid" not in res_e["case_ids"]
    assert res_e["evidence"]["C_last"]["highlight_positions"] == [2]


def test_mean_cycle_time_uses_full_trace_not_filtered_subset():
    """Cycle time dihitung dari durasi full case trace, bukan dari subset event hasil filter."""
    # Case C1: event jam 08:00, 09:00 (Accepted), 12:00 (event akhir).
    # Durasi full trace = 4 jam (4/24 hari = 0.16667 hari).
    # Jika hanya event Accepted (09:00), durasinya akan 0 hari (salah).
    log = make_log({
        "C1": ["A_Create", "O_Accepted", "W_Call", "W_Validate", "W_Finish"],
    })
    res_c = exercise_117_c(log.df)
    expected_days = 4.0 / 24.0
    assert res_c["evidence"]["C1"]["duration_days"] == pytest.approx(expected_days)
    assert res_c["metrics"]["mean_cycle_days"] == pytest.approx(expected_days)


def test_single_event_and_same_timestamp_duration_zero():
    """Case 1 event: 0 hari; case dengan timestamp sama: 0 hari."""
    log = make_log({
        "C_single": ["O_Cancelled"],
    })
    durations = case_durations_days(log.df)
    assert durations["C_single"] == 0.0

    res_e = exercise_117_e(log.df)
    assert res_e["case_ids"] == ["C_single"]
    assert res_e["evidence"]["C_single"]["duration_days"] == 0.0
    assert res_e["metrics"]["mean_cycle_days"] == 0.0


def test_empty_group_returns_none_mean_not_zero():
    """Kelompok tanpa case menghasilkan case_count=0 dan mean_cycle_days=None (bukan 0.0)."""
    log = make_log({
        "C1": ["A_Create", "W_Call"],
    })
    res_c = exercise_117_c(log.df)
    assert res_c["case_count"] == 0
    assert res_c["case_ids"] == []
    assert res_c["metrics"]["mean_cycle_days"] is None
    assert res_c["metrics"]["percentage"] == 0.0

    res_d = exercise_117_d(log.df)
    assert res_d["case_count"] == 0
    assert res_d["metrics"]["mean_cycle_days"] is None

    res_e = exercise_117_e(log.df)
    assert res_e["case_count"] == 0
    assert res_e["metrics"]["mean_cycle_days"] is None


def test_sample_log_xes_117_exact_numbers():
    """Assertion testing pada sample_data/sample_log.xes sesuai tabel acuan dosen/spesifikasi."""
    log = load_log(str(SAMPLE_XES))
    results = exercise_117_all(log.df)

    res_a = results["11.7 A"]
    res_b = results["11.7 B"]
    res_c = results["11.7 C"]
    res_d = results["11.7 D"]
    res_e = results["11.7 E"]

    # 11.7 A: 10 case
    assert res_a["case_count"] == 10
    assert len(res_a["case_ids"]) == 10

    # 11.7 B: denominator 10, mean 0.0541666666667 hari (13 / 240 hari)
    assert res_b["metrics"]["denominator"] == 10
    assert res_b["metrics"]["mean_cycle_days"] == pytest.approx(13.0 / 240.0, rel=1e-5)

    # 11.7 C: 4 case (App 01, 02, 03, 04), mean 0.0729166666667 hari (7 / 96 hari)
    assert res_c["case_count"] == 4
    assert res_c["case_ids"] == ["Application_01", "Application_02", "Application_03", "Application_04"]
    assert res_c["metrics"]["denominator"] == 10
    assert res_c["metrics"]["percentage"] == pytest.approx(40.0)
    assert res_c["metrics"]["mean_cycle_days"] == pytest.approx(7.0 / 96.0, rel=1e-5)

    # 11.7 D: 1 case (App 06), mean 0.0416666666667 hari (1 / 24 hari)
    assert res_d["case_count"] == 1
    assert res_d["case_ids"] == ["Application_06"]
    assert res_d["metrics"]["denominator"] == 10
    assert res_d["metrics"]["percentage"] == pytest.approx(10.0)
    assert res_d["metrics"]["mean_cycle_days"] == pytest.approx(1.0 / 24.0, rel=1e-5)

    # 11.7 E: 3 case (App 02, 03, 05), mean 0.0416666666667 hari (1 / 24 hari)
    assert res_e["case_count"] == 3
    assert res_e["case_ids"] == ["Application_02", "Application_03", "Application_05"]
    assert res_e["metrics"]["denominator"] == 10
    assert res_e["metrics"]["percentage"] == pytest.approx(30.0)
    assert res_e["metrics"]["mean_cycle_days"] == pytest.approx(1.0 / 24.0, rel=1e-5)
