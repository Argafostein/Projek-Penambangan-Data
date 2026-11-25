"""Uji asap GUI tanpa layar (offscreen): impor sampel -> overview -> 11.22 -> explorer -> ekspor."""
import os
import time
from pathlib import Path

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
pytest.importorskip("PySide6")

from PySide6.QtWidgets import QApplication  # noqa: E402

SAMPLE = Path(__file__).resolve().parent.parent / "sample_data" / "sample_log.xes"


def wait_until(app, cond, timeout=30):
    end = time.time() + timeout
    while time.time() < end:
        app.processEvents()
        if cond():
            return True
        time.sleep(0.02)
    return False


def test_end_to_end(tmp_path):
    from gui.main_window import MainWindow
    from gui.workers import shutdown_tasks

    app = QApplication.instance() or QApplication([])
    win = MainWindow()
    win.show()
    win.load_file(str(SAMPLE))
    assert wait_until(app, lambda: win.log is not None)
    assert win.log.n_cases == 10

    assert wait_until(app, lambda: win.overview_panel.card_cases.value.text() == "10")

    win.panel_1122.run()
    assert wait_until(app, lambda: "11.22" in win.results)
    res = win.results["11.22"]
    assert res["case_ids"] == ["Application_01", "Application_03", "Application_04"]
    assert res["metrics"]["denominator"] == 10
    assert win.panel_1122.card_p.value.text() == "30.00%"

    win.open_in_explorer(res, "Application_01")
    assert win.explorer.case_header.text().startswith("<b>Case Application_01")
    assert win.explorer.trace_model.highlight_rows == {0, 2}

    from utils.csv_export import export_cases, export_summary
    assert export_cases(res, str(tmp_path / "c.csv")) == 3
    assert export_summary(win.results, str(tmp_path / "s.csv")) >= 4

    win.reset_all()
    assert win.results == {}
    win.close()
    shutdown_tasks()
