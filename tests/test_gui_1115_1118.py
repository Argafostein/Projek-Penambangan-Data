"""Uji integrasi GUI offscreen untuk panel Exercise 11.15 & 11.18."""
from __future__ import annotations

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


def test_panel_1115_1118_end_to_end(tmp_path):
    from gui.main_window import MainWindow
    from gui.panel_1115_1118 import Panel1115_1118
    from gui.workers import shutdown_tasks
    from utils.csv_export import export_cases, export_summary

    app = QApplication.instance() or QApplication([])
    win = MainWindow()
    assert isinstance(win.panel_1115, Panel1115_1118)
    win.show()

    win.load_file(str(SAMPLE))
    assert wait_until(app, lambda: win.log is not None)

    win.panel_1115.run()
    assert wait_until(app, lambda: "11.15" in win.results and "11.18" in win.results)

    assert win.panel_1115.card_1115_n.value.text() == "3"
    assert win.panel_1115.card_1118_n.value.text() == "1"
    assert win.panel_1115.table_1115.model.rowCount() == 3
    assert win.panel_1115.table_1118.model.rowCount() == 1

    # Filter minimal complete pada tab 11.15
    win.panel_1115.min_complete_spin.setValue(3)
    assert win.panel_1115.table_1115.model.rowCount() == 0
    win.panel_1115.min_complete_spin.setValue(2)
    assert win.panel_1115.table_1115.model.rowCount() == 3

    # Filter resource pada tab 11.18
    win.panel_1115.resource_filter.setText("User_999")
    assert win.panel_1115.table_1118.model.rowCount() == 0
    win.panel_1115.resource_filter.setText("User_4")
    assert win.panel_1115.table_1118.model.rowCount() == 1

    # Buka evidence 11.18 di Case Explorer
    res18 = win.results["11.18"]
    win.open_in_explorer(res18, "Application_09")
    assert win.explorer.case_header.text().startswith("<b>Case Application_09")
    assert win.explorer.trace_model.highlight_rows == {0, 1}

    # Ekspor CSV
    assert export_cases(win.results["11.15"], str(tmp_path / "1115.csv")) == 3
    assert export_cases(res18, str(tmp_path / "1118.csv")) == 1
    assert export_summary(win.results, str(tmp_path / "summary.csv")) >= 10

    win.reset_all()
    assert win.results == {}
    assert win.panel_1115.card_1115_n.value.text() == "-"
    assert win.panel_1115.card_1118_n.value.text() == "-"

    win.close()
    shutdown_tasks()

