from core.exercise_1122 import exercise_1122
from helpers import make_log


def run(cases):
    return exercise_1122(make_log(cases).df)


def test_non_adjacent_pair_passes():
    r = run({"A": ["O_Cancelled", "W_Call", "O_Accepted"]})
    assert r["case_ids"] == ["A"]


def test_accepted_before_cancelled_fails():
    r = run({"B": ["O_Accepted", "O_Cancelled"]})
    assert r["case_count"] == 0 and r["case_ids"] == []


def test_cancelled_accepted_cancelled_passes():
    assert run({"C": ["O_Cancelled", "O_Accepted", "O_Cancelled"]})["case_ids"] == ["C"]


def test_accepted_cancelled_accepted_passes():
    assert run({"F": ["O_Accepted", "O_Cancelled", "O_Accepted"]})["case_ids"] == ["F"]


def test_only_one_activity_fails():
    r = run({"D": ["O_Cancelled", "W_Call"], "E": ["O_Accepted"]})
    assert r["case_count"] == 0


def test_case_counted_once_even_with_many_pairs():
    r = run({"G": ["O_Cancelled", "O_Accepted", "O_Cancelled", "O_Accepted"]})
    assert r["case_count"] == 1


def test_percentage_uses_all_cases_as_denominator():
    r = run(
        {
            "A": ["O_Cancelled", "O_Accepted"],
            "B": ["O_Accepted", "O_Cancelled"],
            "C": ["X"],
            "D": ["O_Cancelled"],
        }
    )
    m = r["metrics"]
    assert (m["numerator"], m["denominator"]) == (1, 4)
    assert m["percentage"] == 25.0
    assert m["cases_with_both_activities"] == 2


def test_evidence_points_to_nearest_accepted_after_first_cancel():
    r = run({"A": ["O_Accepted", "O_Cancelled", "X", "O_Accepted", "O_Accepted"]})
    ev = r["evidence"]["A"]
    assert (ev["cancelled_position"], ev["accepted_position"]) == (2, 4)
    assert ev["highlight_positions"] == [2, 4]


def test_empty_result_is_valid():
    r = run({"A": ["X", "Y"]})
    assert r["case_count"] == 0 and r["evidence"] == {} and r["metrics"]["percentage"] == 0.0
