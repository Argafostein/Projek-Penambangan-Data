"""Unit test edge case untuk Exercise 11.15, 11.18, dan pemeriksaan lifecycle XES."""
from __future__ import annotations

from pathlib import Path

import pandas as pd

from core.exercise_1115 import exercise_1115
from core.exercise_1118 import exercise_1118
from core.lifecycle import TARGET_ACTIVITY, inspect_lifecycle, is_complete_series
from core.log_loader import load_log
from tests.helpers import make_log

W = TARGET_ACTIVITY
SAMPLE_XES = Path(__file__).resolve().parent.parent / "sample_data" / "sample_log.xes"


def test_scheduled_twice_complete_once_fails_both():
    log = make_log({
        "C1": [
            (W, "schedule", "User_1"),
            (W, "schedule", "User_1"),
            (W, "complete", "User_1"),
        ],
    })
    r15 = exercise_1115(log.df)
    r18 = exercise_1118(log.df)
    assert r15["case_count"] == 0
    assert r18["case_count"] == 0


def test_non_complete_lifecycles_never_counted():
    log = make_log({
        "C1": [
            (W, "schedule", "User_1"),
            (W, "scheduled", "User_1"),
            (W, "start", "User_1"),
            (W, "suspend", "User_1"),
            (W, "resume", "User_1"),
            (W, "ate_abort", "User_1"),
            (W, "pi_abort", "User_1"),
            (W, "withdraw", "User_1"),
            (W, None, "User_1"),
            (W, "   ", "User_1"),
            (W, "complete", "User_1"),
        ],
    })
    r15 = exercise_1115(log.df)
    r18 = exercise_1118(log.df)
    assert r15["case_count"] == 0
    assert r18["case_count"] == 0
    assert r15["lifecycle_info"]["target_complete_events"] == 1
    assert r15["lifecycle_info"]["target_non_complete_events"] == 10


def test_complete_lifecycle_is_case_insensitive_and_trimmed():
    log = make_log({
        "C1": [
            (W, "Complete", "User_1"),
            (W, " complete ", "User_1"),
        ],
    })
    r15 = exercise_1115(log.df)
    r18 = exercise_1118(log.df)
    assert r15["case_ids"] == ["C1"]
    assert r18["case_ids"] == ["C1"]


def test_missing_lifecycle_attribute_does_not_assume_complete():
    df = pd.DataFrame([
        {
            "case_id": "C1",
            "activity": W,
            "timestamp": pd.Timestamp("2016-01-01 08:00:00", tz="UTC"),
            "lifecycle": None,
            "resource": "User_1",
            "position": 1,
        },
        {
            "case_id": "C1",
            "activity": W,
            "timestamp": pd.Timestamp("2016-01-01 09:00:00", tz="UTC"),
            "lifecycle": None,
            "resource": "User_1",
            "position": 2,
        },
    ])
    info = inspect_lifecycle(df)
    assert info["has_lifecycle"] is False
    assert info["source_attribute"] == "tidak tersedia"
    assert not is_complete_series(df).any()
    assert exercise_1115(df)["case_count"] == 0
    assert exercise_1118(df)["case_count"] == 0


def test_different_resources_pass_1115_but_fail_1118():
    log = make_log({
        "C_diff": [
            (W, "complete", "User_1"),
            (W, "complete", "User_2"),
        ],
    })
    r15 = exercise_1115(log.df)
    r18 = exercise_1118(log.df)
    assert r15["case_ids"] == ["C_diff"]
    assert r18["case_ids"] == []
    assert r18["metrics"]["cases_passing_1115"] == 1
    assert r18["metrics"]["cases_excluded_diff_or_null_resource"] == 1


def test_empty_or_null_resources_never_considered_same():
    log = make_log({
        "C_none": [
            (W, "complete", None),
            (W, "complete", None),
        ],
        "C_blank": [
            (W, "complete", ""),
            (W, "complete", "   "),
        ],
    })
    r15 = exercise_1115(log.df)
    r18 = exercise_1118(log.df)
    assert r15["case_ids"] == ["C_blank", "C_none"]
    assert r18["case_ids"] == []
    assert r18["metrics"]["total_complete_with_null_resource"] == 4


def test_same_identified_resource_passes_both_and_ignores_extra_null():
    log = make_log({
        "C_ok": [
            (W, "complete", None),
            (W, "complete", "User_4"),
            (W, "schedule", "User_4"),
            (W, "complete", "User_4"),
        ],
    })
    r15 = exercise_1115(log.df)
    r18 = exercise_1118(log.df)
    assert r15["case_ids"] == ["C_ok"]
    assert r15["evidence"]["C_ok"]["complete_count"] == 3
    assert r15["evidence"]["C_ok"]["highlight_positions"] == [1, 2, 4]

    assert r18["case_ids"] == ["C_ok"]
    assert r18["evidence"]["C_ok"]["primary_resource"] == "User_4"
    assert r18["evidence"]["C_ok"]["max_complete_by_same_resource"] == 2
    assert r18["evidence"]["C_ok"]["highlight_positions"] == [2, 4]


def test_case_counted_once_even_with_multiple_qualifying_resources():
    log = make_log({
        "C_multi": [
            (W, "complete", "User_A"),
            (W, "complete", "User_B"),
            (W, "complete", "User_A"),
            (W, "complete", "User_B"),
            (W, "complete", "User_B"),
        ],
    })
    r15 = exercise_1115(log.df)
    r18 = exercise_1118(log.df)
    assert r15["case_count"] == 1
    assert r15["evidence"]["C_multi"]["complete_count"] == 5

    assert r18["case_count"] == 1
    assert r18["evidence"]["C_multi"]["primary_resource"] == "User_B"
    assert r18["evidence"]["C_multi"]["max_complete_by_same_resource"] == 3
    assert set(r18["evidence"]["C_multi"]["qualifying_resources"]) == {"User_A", "User_B"}


def test_other_activities_are_ignored():
    log = make_log({
        "C_other": [
            ("W_Call after offers", "complete", "User_1"),
            ("W_Call after offers", "complete", "User_1"),
            (W, "complete", "User_1"),
        ],
    })
    assert exercise_1115(log.df)["case_count"] == 0
    assert exercise_1118(log.df)["case_count"] == 0


def test_sample_log_xes_expected_cases():
    log = load_log(str(SAMPLE_XES))
    r15 = exercise_1115(log.df)
    r18 = exercise_1118(log.df)

    # Application_07: schedule 2x, complete 1x -> gagal
    # Application_08: complete 2x resource beda -> lolos 11.15, gagal 11.18
    # Application_09: complete 2x resource sama (User_4) -> lolos keduanya
    # Application_10: complete 2x resource kosong -> lolos 11.15, gagal 11.18
    assert r15["case_ids"] == ["Application_08", "Application_09", "Application_10"]
    assert r15["metrics"]["denominator"] == 10
    assert r18["case_ids"] == ["Application_09"]
    assert r18["evidence"]["Application_09"]["primary_resource"] == "User_4"
    assert r18["metrics"]["cases_excluded_diff_or_null_resource"] == 2

