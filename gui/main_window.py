"""Jendela utama: navigasi, status bar, pemuatan log di thread latar belakang, dan perekat antar panel.

Alur: Impor XES -> Overview -> Pilih Latihan -> Jalankan -> Lihat Jawaban -> Periksa Case -> Ekspor.
Panel milik Lintang (11.7) dan Arga (11.15/11.18) dimuat otomatis jika filenya sudah ada.
"""
from __future__ import annotations

import importlib

from PySide6.QtGui import QAction, QKeySequence
from PySide6.QtWidgets import (
    QHBoxLayout, QLabel, QListWidget, QMainWindow, QMessageBox, QProgressBar, QStackedWidget, QVBoxLayout, QWidget,
)

from core.log_loader import LogData, load_log
from gui.case_explorer import CaseExplorer
from gui.panel_1122 import Panel1122
from gui.panel_base import AnalysisPanelBase
from gui.panel_dataset import DatasetPanel
from gui.panel_export import ExportPanel
from gui.panel_overview import OverviewPanel
from gui.workers import run_task, shutdown_tasks
from utils.versions import get_versions


class PlaceholderPanel(AnalysisPanelBase):
    def __init__(self, title: str, message: str, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        label = QLabel(f"<h2>{title}</h2><p>{message}</p>")
        label.setWordWrap(True)
        layout.addWidget(label)
        layout.addStretch(1)


def load_external_panel(module_name: str, class_name: str, title: str) -> QWidget:
    """Muat panel anggota lain; jika belum ada, tampilkan placeholder (aplikasi tetap jalan)."""
    try:
        return getattr(importlib.import_module(module_name), class_name)()
    except ModuleNotFoundError as exc:
        if exc.name == module_name:
            return PlaceholderPanel(title, f"Modul <code>{module_name}</code> belum tersedia.")
        return PlaceholderPanel(title, f"Gagal memuat <code>{module_name}</code>: {exc}")
    except Exception as exc:  # noqa: BLE001
        return PlaceholderPanel(title, f"Gagal memuat <code>{module_name}</code>: {exc}")


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("BPIC17 Event Log Analyzer - Tahap 1")
        self.resize(1200, 780)
        self.log: LogData | None = None
        self.results: dict = {}
        self._loading = False

        self.dataset_panel = DatasetPanel()
        self.overview_panel = OverviewPanel()
        self.panel_117 = load_external_panel("gui.panel_117", "Panel117", "Exercise 11.7")
        self.panel_1115 = load_external_panel("gui.panel_1115_1118", "Panel1115_1118", "Exercise 11.15 & 11.18")
        self.panel_1122 = Panel1122()
        self.explorer = CaseExplorer()
        self.export_panel = ExportPanel()

        self.pages = [
            ("Dataset & Status", self.dataset_panel),
            ("Overview", self.overview_panel),
            ("Exercise 11.7", self.panel_117),
            ("Exercise 11.15 & 11.18", self.panel_1115),
            ("Exercise 11.22", self.panel_1122),
            ("Case Explorer", self.explorer),
            ("Export", self.export_panel),
        ]
        self.analysis_panels = [self.overview_panel, self.panel_117, self.panel_1115, self.panel_1122]

        self.nav = QListWidget()
        self.nav.setFixedWidth(210)
        self.stack = QStackedWidget()
        for label, widget in self.pages:
            self.nav.addItem(label)
            self.stack.addWidget(widget)
        self.nav.currentRowChanged.connect(self.stack.setCurrentIndex)

        central = QWidget()
        layout = QHBoxLayout(central)
        layout.addWidget(self.nav)
        layout.addWidget(self.stack, 1)
        self.setCentralWidget(central)

        self.status_label = QLabel("Siap. Impor file XES untuk memulai.")
        self.progress = QProgressBar()
        self.progress.setFixedWidth(160)
        self.progress.setRange(0, 0)  # indeterminate: PM4Py tidak melaporkan persentase
        self.progress.hide()
        self.statusBar().addWidget(self.status_label, 1)
        self.statusBar().addPermanentWidget(self.progress)

        self.dataset_panel.file_chosen.connect(self.load_file)
        for panel in self.analysis_panels:
            if hasattr(panel, "result_ready"):
                panel.result_ready.connect(self.register_result)
            if hasattr(panel, "show_in_explorer"):
                panel.show_in_explorer.connect(self.open_in_explorer)
            if hasattr(panel, "status_message"):
                panel.status_message.connect(self.status_label.setText)

        self._build_menu()
        self.nav.setCurrentRow(0)

    def _build_menu(self) -> None:
        file_menu = self.menuBar().addMenu("&File")
        open_act = QAction("Buka file XES...", self)
        open_act.setShortcut(QKeySequence.StandardKey.Open)
        open_act.triggered.connect(self.dataset_panel.choose_file)
        reset_act = QAction("Reset semua hasil analisis", self)
        reset_act.triggered.connect(self.reset_all)
        quit_act = QAction("Keluar", self)
        quit_act.triggered.connect(self.close)
        file_menu.addAction(open_act)
        file_menu.addAction(reset_act)
        file_menu.addSeparator()
        file_menu.addAction(quit_act)
        help_menu = self.menuBar().addMenu("&Bantuan")
        about_act = QAction("Tentang / versi library", self)
        about_act.triggered.connect(self.show_about)
        help_menu.addAction(about_act)

    # ---- pemuatan log ----
    def _set_busy(self, busy: bool, text: str = "") -> None:
        self.progress.setVisible(busy)
        if text:
            self.status_label.setText(text)

    def load_file(self, path: str) -> None:
        if self._loading:
            return
        self._loading = True
        self.dataset_panel.set_busy(True)
        self.dataset_panel.append_message(f"Mulai mengimpor: {path}")
        self._set_busy(True, "Mengimpor file XES...")
        run_task(
            load_log, path, with_progress=True,
            on_success=self._on_loaded, on_error=self._on_load_failed, on_status=self._on_status,
        )

    def _on_status(self, text: str) -> None:
        self.status_label.setText(text)
        self.dataset_panel.append_message(text)

    def _on_loaded(self, log: LogData) -> None:
        self._loading = False
        self.log = log
        self.results = {}
        for panel in self.analysis_panels:
            if hasattr(panel, "set_log"):
                panel.set_log(log)
        self.explorer.set_log(log)
        self.export_panel.set_results({})
        self.dataset_panel.set_busy(False)
        self.dataset_panel.show_loaded(log)
        self._set_busy(False, f"Impor selesai: {log.n_cases:,} case, {log.n_events:,} event.")
        self.nav.setCurrentRow(1)  # lanjut ke Overview

    def _on_load_failed(self, message: str) -> None:
        self._loading = False
        self.dataset_panel.set_busy(False)
        self.dataset_panel.show_error(message)
        self._set_busy(False, "Impor gagal.")
        QMessageBox.critical(self, "Gagal mengimpor", message + "\n\nLog sebelumnya (jika ada) tetap aktif.")

    # ---- hasil analisis ----
    def register_result(self, result: dict) -> None:
        self.results[result["exercise"]] = result
        self.explorer.set_results(self.results)
        self.export_panel.set_results(self.results)

    def open_in_explorer(self, result: dict, case_id: str) -> None:
        self.explorer.show_result(result, case_id)
        self.nav.setCurrentRow(5)

    def reset_all(self) -> None:
        self.results = {}
        for panel in self.analysis_panels:
            if panel is not self.overview_panel and hasattr(panel, "reset"):
                panel.reset()
        self.explorer.set_results({})
        self.export_panel.set_results({})
        self.status_label.setText("Semua hasil analisis direset. Log aktif tetap dimuat.")

    def show_about(self) -> None:
        lines = "<br>".join(f"{k}: {v}" for k, v in get_versions().items())
        QMessageBox.about(
            self, "Tentang",
            f"<b>BPIC17 Event Log Analyzer - Tahap 1</b><br><br>{lines}",
        )

    def closeEvent(self, event) -> None:
        shutdown_tasks()
        super().closeEvent(event)
