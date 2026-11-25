import pytest

from core.log_loader import LogLoadError, load_log
from helpers import make_log, xes_text


def write(tmp_path, name, text):
    p = tmp_path / name
    p.write_text(text, encoding="utf-8")
    return str(p)


def test_load_valid_xes(tmp_path):
    cases = {
        "C1": [("A_Create", "complete", "User_1"), ("O_Accepted", "complete", "")],
        "C2": [("A_Create", "complete", None)],
    }
    log = load_log(write(tmp_path, "ok.xes", xes_text(cases)))
    assert (log.n_cases, log.n_events) == (2, 3)
    assert log.has_lifecycle and log.has_resource
    assert list(log.df["position"]) == [1, 2, 1]
    assert log.df["resource"].isna().tolist() == [False, True, True]  # resource kosong -> NaN
    assert "concept:name" in log.attributes


def test_file_not_found():
    with pytest.raises(LogLoadError, match="tidak ditemukan"):
        load_log("/tidak/ada.xes")


def test_wrong_extension(tmp_path):
    with pytest.raises(LogLoadError, match=".xes"):
        load_log(write(tmp_path, "x.txt", "halo"))


def test_missing_timestamp(tmp_path):
    text = xes_text({"C1": [("A", "complete", None)]}, with_timestamp=False)
    with pytest.raises(LogLoadError, match="time:timestamp"):
        load_log(write(tmp_path, "nots.xes", text))


def test_corrupted_file(tmp_path):
    with pytest.raises(LogLoadError):
        load_log(write(tmp_path, "rusak.xes", "<log><trace><event>"))


def test_optional_columns_absent():
    log = make_log({"A": [("X", None, None)]})
    assert not log.has_lifecycle and not log.has_resource


def test_case_trace_order():
    log = make_log({"A": ["X", "Y", "Z"], "B": ["Q"]})
    t = log.case_trace("A")
    assert list(t["activity"]) == ["X", "Y", "Z"] and list(t["position"]) == [1, 2, 3]
