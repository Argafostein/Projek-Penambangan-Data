"""Mengambil screenshot nyata dari seluruh panel GUI aplikasi menggunakan Qt offscreen.
Simpan gambar ke docs/screenshots/.
"""
from __future__ import annotations

import os
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtCore import QSize
from PySide6.QtWidgets import QApplication

from core.log_loader import load_log
from gui.main_window import MainWindow
from gui.workers import shutdown_tasks

SAMPLE_XES = ROOT / "sample_data" / "sample_log.xes"
OUT_DIR = ROOT / "docs" / "screenshots"


def wait_events(app, count=25, delay=0.03):
    for _ in range(count):
        app.processEvents()
        time.sleep(delay)


def capture_all():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    app = QApplication.instance() or QApplication(sys.argv)
    
    win = MainWindow()
    win.resize(1200, 780)
    win.show()
    wait_events(app, 10)

    # Muat file log secara sinkron/langsung agar terjamin loaded
    log = load_log(str(SAMPLE_XES))
    win._on_loaded(log)
    wait_events(app, 15)

    # Screenshot 1: Dataset & Status
    win.nav.setCurrentRow(0)
    wait_events(app, 10)
    win.grab().save(str(OUT_DIR / "01_dataset_status.png"))
    print("Saved 01_dataset_status.png")

    # Screenshot 2: Overview
    win.nav.setCurrentRow(1)
    wait_events(app, 10)
    win.grab().save(str(OUT_DIR / "02_overview.png"))
    print("Saved 02_overview.png")

    # Jalankan seluruh analisis
    win.panel_117.run()
    win.panel_1115.run()
    win.panel_1122.run()
    
    # Tunggu seluruh task selesai di background threads
    end = time.time() + 15
    while time.time() < end:
        app.processEvents()
        if (
            "11.7 A" in win.results
            and "11.15" in win.results
            and "11.18" in win.results
            and "11.22" in win.results
        ):
            break
        time.sleep(0.05)
    wait_events(app, 15)

    # Screenshot 3: Exercise 11.7 C
    win.nav.setCurrentRow(2)
    win.panel_117.tabs.setCurrentIndex(2)  # Tab 11.7 C (Successful cases)
    wait_events(app, 10)
    win.grab().save(str(OUT_DIR / "03_exercise_117_c.png"))
    print("Saved 03_exercise_117_c.png")

    # Screenshot 3b: Exercise 11.7 E
    win.panel_117.tabs.setCurrentIndex(4)  # Tab 11.7 E (Canceled endpoint)
    wait_events(app, 10)
    win.grab().save(str(OUT_DIR / "03_exercise_117_e.png"))
    print("Saved 03_exercise_117_e.png")

    # Screenshot 4: Exercise 11.15
    win.nav.setCurrentRow(3)
    win.panel_1115.tabs.setCurrentIndex(0)
    wait_events(app, 10)
    win.grab().save(str(OUT_DIR / "04_exercise_1115.png"))
    print("Saved 04_exercise_1115.png")

    # Screenshot 5: Exercise 11.18
    win.nav.setCurrentRow(3)
    win.panel_1115.tabs.setCurrentIndex(1)
    wait_events(app, 10)
    win.grab().save(str(OUT_DIR / "05_exercise_1118.png"))
    print("Saved 05_exercise_1118.png")

    # Screenshot 6: Exercise 11.22
    win.nav.setCurrentRow(4)
    wait_events(app, 10)
    win.grab().save(str(OUT_DIR / "06_exercise_1122.png"))
    print("Saved 06_exercise_1122.png")

    # Screenshot 7: Case Explorer untuk 11.15 (Application_08)
    win.open_in_explorer(win.results["11.15"], "Application_08")
    wait_events(app, 15)
    win.grab().save(str(OUT_DIR / "07_case_explorer_1115.png"))
    print("Saved 07_case_explorer_1115.png")

    # Screenshot 8: Case Explorer untuk 11.18 (Application_09 - Same Resource)
    win.open_in_explorer(win.results["11.18"], "Application_09")
    wait_events(app, 15)
    win.grab().save(str(OUT_DIR / "08_case_explorer_1118.png"))
    print("Saved 08_case_explorer_1118.png")

    # Screenshot 9: Case Explorer untuk 11.22 (Application_01 - Cancelled then Accepted)
    win.open_in_explorer(win.results["11.22"], "Application_01")
    wait_events(app, 15)
    win.grab().save(str(OUT_DIR / "09_case_explorer_1122.png"))
    print("Saved 09_case_explorer_1122.png")

    # Screenshot 10: Export Panel
    win.nav.setCurrentRow(6)
    wait_events(app, 10)
    win.grab().save(str(OUT_DIR / "10_export_panel.png"))
    print("Saved 10_export_panel.png")

    win.close()
    shutdown_tasks()
    print("Semua screenshot berhasil dibuat di:", OUT_DIR)


if __name__ == "__main__":
    capture_all()
