"""F02 (sisi GUI) - Overview: metrik dasar, frekuensi aktivitas, daftar case & durasi."""
from __future__ import annotations

from PySide6.QtWidgets import QHBoxLayout, QLabel, QTabWidget, QVBoxLayout

from core.overview import Overview, compute_overview
from gui.panel_base import AnalysisPanelBase
from gui.widgets import MetricCard, SearchableTable, fmt_int
from gui.workers import run_task


class OverviewPanel(AnalysisPanelBase):
    def __init__(self, parent=None):
        super().__init__(parent)
        root = QVBoxLayout(self)
        root.addWidget(QLabel("<h2>Overview Event Log</h2>"))

        cards = QHBoxLayout()
        self.card_cases = MetricCard("Total case")
        self.card_events = MetricCard("Total event")
        self.card_range = MetricCard("Rentang waktu (UTC)")
        self.card_mean = MetricCard("Rata-rata cycle time")
        for c in (self.card_cases, self.card_events, self.card_range, self.card_mean):
            cards.addWidget(c)
        root.addLayout(cards)

        note = QLabel(
            "Cycle time = timestamp event terakhir - event pertama pada tiap case. "
            "Satuan: hari (1 hari = 24 jam), ditampilkan 4 desimal, disimpan penuh. "
            "Seluruh timestamp dinormalisasi ke UTC."
        )
        note.setWordWrap(True)
        root.addWidget(note)
        self.state_label = QLabel("Impor file XES terlebih dahulu.")
        root.addWidget(self.state_label)

        tabs = QTabWidget()
        self.activity_table = SearchableTable("Cari aktivitas...")
        self.case_table = SearchableTable("Cari case ID...")
        self.case_table.row_activated.connect(lambda cid: self.show_in_explorer.emit({}, cid))
        tabs.addTab(self.activity_table, "Frekuensi aktivitas")
        tabs.addTab(self.case_table, "Daftar case & durasi (double-click untuk rincian)")
        root.addWidget(tabs, 1)

    def set_log(self, log) -> None:
        super().set_log(log)
        if log is not None:
            self.state_label.setText("Menghitung overview...")
            run_task(compute_overview, log, on_success=self._show, on_error=self._failed)

    def reset(self) -> None:
        for c in (self.card_cases, self.card_events, self.card_range, self.card_mean):
            c.set_value("-")
        self.activity_table.clear()
        self.case_table.clear()

    def _failed(self, message: str) -> None:
        self.state_label.setText("Overview gagal: " + message)

    def _show(self, ov: Overview) -> None:
        if ov.source is not self.log:  # hasil dari file lama, abaikan
            return
        self.state_label.setText("")
        self.card_cases.set_value(fmt_int(ov.total_cases))
        self.card_events.set_value(fmt_int(ov.total_events))
        self.card_range.set_value(
            f"{ov.first_timestamp:%Y-%m-%d} s/d {ov.last_timestamp:%Y-%m-%d}"
        )
        self.card_mean.set_value(
            "-" if ov.mean_cycle_days is None else f"{ov.mean_cycle_days:.4f} hari"
        )
        self.activity_table.set_dataframe(ov.activity_table)
        self.case_table.set_dataframe(ov.case_table)
        self.status_message.emit("Overview selesai dihitung.")
