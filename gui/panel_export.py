"""F07 (sisi GUI) - Ekspor ringkasan jawaban dan daftar case terpilih ke CSV."""
from __future__ import annotations

import re

from PySide6.QtWidgets import QComboBox, QFileDialog, QHBoxLayout, QLabel, QMessageBox, QPushButton, QVBoxLayout, QWidget

from gui.widgets import fmt_int
from utils.csv_export import export_cases, export_summary


class ExportPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.results: dict = {}
        root = QVBoxLayout(self)
        root.addWidget(QLabel("<h2>Export</h2>"))
        self.info = QLabel("")
        self.info.setWordWrap(True)
        root.addWidget(self.info)

        self.summary_btn = QPushButton("Ekspor ringkasan jawaban (CSV)")
        self.summary_btn.clicked.connect(self._export_summary)
        root.addWidget(self.summary_btn)

        row = QHBoxLayout()
        row.addWidget(QLabel("Daftar case dari analisis:"))
        self.combo = QComboBox()
        row.addWidget(self.combo, 1)
        self.cases_btn = QPushButton("Ekspor daftar case (CSV)")
        self.cases_btn.clicked.connect(self._export_cases)
        row.addWidget(self.cases_btn)
        root.addLayout(row)

        self.message = QLabel("")
        self.message.setWordWrap(True)
        root.addWidget(self.message)
        root.addStretch(1)
        self.set_results({})

    def set_results(self, results: dict) -> None:
        self.results = dict(results)
        self.combo.clear()
        for key in sorted(self.results):
            self.combo.addItem(f"{key} - {fmt_int(self.results[key]['case_count'])} case", key)
        has = bool(self.results)
        self.summary_btn.setEnabled(has)
        self.cases_btn.setEnabled(has)
        self.info.setText(
            f"Analisis yang sudah dijalankan: {', '.join(sorted(self.results))}."
            if has else "Belum ada hasil analisis. Jalankan analisis pada menu latihan terlebih dahulu."
        )

    def _ask_path(self, title: str, default: str) -> str:
        path, _ = QFileDialog.getSaveFileName(self, title, default, "File CSV (*.csv)")
        if path and not path.lower().endswith(".csv"):
            path += ".csv"
        return path

    def _export_summary(self) -> None:
        path = self._ask_path("Simpan ringkasan jawaban", "ringkasan_jawaban.csv")
        if path:
            self._run(lambda: export_summary(self.results, path), path)

    def _export_cases(self) -> None:
        key = self.combo.currentData()
        if key is None:
            return
        safe = re.sub(r"[^\w.-]+", "_", key)
        path = self._ask_path("Simpan daftar case", f"daftar_case_{safe}.csv")
        if path:
            self._run(lambda: export_cases(self.results[key], path), path)

    def _run(self, action, path: str) -> None:
        try:
            n = action()
        except OSError as exc:
            QMessageBox.critical(self, "Gagal menyimpan", f"File tidak dapat ditulis:\n{exc}")
            return
        self.message.setText(f"Tersimpan: {path} ({fmt_int(n)} baris data)")
