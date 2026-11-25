"""Uji integrasi GUI offscreen untuk panel Exercise 11.7 (A-E)."""
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


def test_panel_117_end_to_end(tmp_path):
    from gui.main_window import MainWindow
    from gui.panel_117 import Panel117
    from gui.workers import shutdown_tasks
    from utils.csv_export import export_cases, export_summary

    app = QApplication.instance() or QApplication([])
    win = MainWindow()
    # Pastikan panel 11.7 BUKAN PlaceholderPanel
    assert isinstance(win.panel_117, Panel117)
    win.show()

    # Muat log
    win.load_file(str(SAMPLE))
    assert wait_until(app, lambda: win.log is not None)
    assert win.log.n_cases == 10

    # Jalankan analisis 11.7
    win.panel_117.run()
    assert wait_until(
        app,
        lambda: all(
            k in win.results
            for k in ("11.7 A", "11.7 B", "11.7 C", "11.7 D", "11.7 E")
        ),
    )

    # Verifikasi kartu
    assert win.panel_117.card_top_a.value.text() == "10"
    assert win.panel_117.card_c_n.value.text() == "4"
    assert win.panel_117.card_d_n.value.text() == "1"
    assert win.panel_117.card_e_n.value.text() == "3"

    # Verifikasi tabel di tiap tab
    assert win.panel_117.table_a.model.rowCount() == 10
    assert win.panel_117.table_b.model.rowCount() == 10
    assert win.panel_117.table_c.model.rowCount() == 4
    assert win.panel_117.table_d.model.rowCount() == 1
    assert win.panel_117.table_e.model.rowCount() == 3

    # Buka evidence 11.7 C di Case Explorer
    res_c = win.results["11.7 C"]
    win.open_in_explorer(res_c, "Application_01")
    assert win.explorer.case_header.text().startswith("<b>Case Application_01")
    # Application_01 memiliki O_Accepted di posisi ke-3 (baris indeks ke-2)
    assert 2 in win.explorer.trace_model.highlight_rows

    # Ekspor CSV
    assert export_cases(win.results["11.7 C"], str(tmp_path / "117c.csv")) == 4
    assert export_summary(win.results, str(tmp_path / "summary_117.csv")) >= 5

    # Reset
    win.reset_all()
    assert win.results == {}
    assert win.panel_117.card_top_a.value.text() == "-"
    assert win.panel_117.card_c_n.value.text() == "-"

    win.close()
    shutdown_tasks()
