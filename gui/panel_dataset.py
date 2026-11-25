"""F01 (sisi GUI) - Dataset & Status: pilih file XES, status impor, atribut tersedia."""
from __future__ import annotations

from datetime import datetime

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QFileDialog, QHBoxLayout, QLabel, QListWidget, QPlainTextEdit, QPushButton, QVBoxLayout, QWidget,
)

from core.log_loader import REQUIRED, XES_NAME, LogData
from gui.widgets import MetricCard, fmt_int


class DatasetPanel(QWidget):
    file_chosen = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        root = QVBoxLayout(self)
        root.addWidget(QLabel("<h2>Dataset & Status</h2>"))

        row = QHBoxLayout()
        self.open_btn = QPushButton("Pilih file .xes...")
        self.open_btn.clicked.connect(self.choose_file)
        self.file_label = QLabel("Belum ada file yang diimpor.")
        self.file_label.setWordWrap(True)
        row.addWidget(self.open_btn)
        row.addWidget(self.file_label, 1)
        root.addLayout(row)

        self.status_label = QLabel("Status: menunggu file")
        root.addWidget(self.status_label)

        cards = QHBoxLayout()
        self.card_cases = MetricCard("Jumlah case")
        self.card_events = MetricCard("Jumlah event")
        self.card_lifecycle = MetricCard("lifecycle:transition")
        self.card_resource = MetricCard("org:resource")
        for c in (self.card_cases, self.card_events, self.card_lifecycle, self.card_resource):
            cards.addWidget(c)
        root.addLayout(cards)

        root.addWidget(QLabel("Atribut yang tersedia pada log:"))
        self.attr_list = QListWidget()
        self.attr_list.setMaximumHeight(150)
        root.addWidget(self.attr_list)

        root.addWidget(QLabel("Pesan proses:"))
        self.messages = QPlainTextEdit()
        self.messages.setReadOnly(True)
        root.addWidget(self.messages, 1)

    def choose_file(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self, "Pilih file event log", "", "Event log XES (*.xes *.xes.gz);;Semua file (*)"
        )
        if path:
            self.file_chosen.emit(path)

    def append_message(self, text: str) -> None:
        self.messages.appendPlainText(f"[{datetime.now():%H:%M:%S}] {text}")

    def set_busy(self, busy: bool, text: str = "") -> None:
        self.open_btn.setEnabled(not busy)
        if busy:
            self.status_label.setText("Status: mengimpor... " + text)

    def show_loaded(self, log: LogData) -> None:
        self.file_label.setText(f"{log.file_name}\n{log.path}")
        self.status_label.setText("Status: impor berhasil")
        self.card_cases.set_value(fmt_int(log.n_cases))
        self.card_events.set_value(fmt_int(log.n_events))
        self.card_lifecycle.set_value("terdeteksi" if log.has_lifecycle else "tidak ada")
        self.card_resource.set_value("terdeteksi" if log.has_resource else "tidak ada")
        self.attr_list.clear()
        self.attr_list.addItems(log.attributes)
        self.append_message(f"Impor berhasil: {fmt_int(log.n_cases)} case, {fmt_int(log.n_events)} event.")
        for name in REQUIRED:
            self.append_message(f"Atribut wajib {XES_NAME[name]}: OK")
        self.append_message(
            "lifecycle:transition " + ("terdeteksi." if log.has_lifecycle else "TIDAK ditemukan (analisis 'complete' tidak dapat dibedakan).")
        )
        self.append_message(
            "org:resource " + ("terdeteksi." if log.has_resource else "TIDAK ditemukan (analisis resource tidak dapat dilakukan).")
        )

    def show_error(self, message: str) -> None:
        self.status_label.setText("Status: impor gagal")
        self.append_message("GAGAL: " + message)
