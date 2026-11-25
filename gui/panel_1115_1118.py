"""F04 & F05 (sisi GUI) - Exercise 11.15 & 11.18: Repeated Complete & Same-Resource Complete."""
from __future__ import annotations

import pandas as pd
from PySide6.QtWidgets import (
    QHBoxLayout, QLabel, QLineEdit, QMessageBox, QPushButton, QSpinBox, QTabWidget, QVBoxLayout, QWidget,
)

from core.exercise_1115 import FILTER_RULE as RULE_1115, exercise_1115
from core.exercise_1118 import FILTER_RULE as RULE_1118, exercise_1118
from gui.panel_base import AnalysisPanelBase
from gui.widgets import MetricCard, SearchableTable, fmt_int, format_value
from gui.workers import run_task

COLS_1115 = [
    "case_id",
    "Jumlah Complete",
    "Waktu Pertama",
    "Waktu Terakhir",
    "Posisi Event",
    "Resource",
]
COLS_1118 = [
    "case_id",
    "Resource Utama",
    "Jumlah Complete (Sama)",
    "Rincian Resource",
    "Posisi Event",
    "Waktu Bukti",
]


def _compute(log):
    return log, exercise_1115(log.df), exercise_1118(log.df)


class Panel1115_1118(AnalysisPanelBase):
    """Panel GUI untuk Exercise 11.15 dan Exercise 11.18 dalam dua tab terpisah."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.result_1115: dict | None = None
        self.result_1118: dict | None = None
        self._df_1115 = pd.DataFrame(columns=COLS_1115)
        self._df_1118 = pd.DataFrame(columns=COLS_1118)

        root = QVBoxLayout(self)
        root.addWidget(QLabel("<h2>Exercise 11.15 &amp; 11.18 - Repeated Complete &amp; Same Resource</h2>"))

        buttons = QHBoxLayout()
        self.run_btn = QPushButton("Jalankan analisis 11.15 & 11.18")
        self.reset_btn = QPushButton("Reset hasil")
        self.explorer_btn = QPushButton("Buka di Case Explorer")
        self.run_btn.clicked.connect(self.run)
        self.reset_btn.clicked.connect(self.reset)
        self.explorer_btn.clicked.connect(self._open_explorer)
        for b in (self.run_btn, self.reset_btn, self.explorer_btn):
            buttons.addWidget(b)
        buttons.addStretch(1)
        root.addLayout(buttons)

        self.lifecycle_banner = QLabel("Status lifecycle XES akan diperiksa saat analisis dijalankan.")
        self.lifecycle_banner.setWordWrap(True)
        root.addWidget(self.lifecycle_banner)

        self.tabs = QTabWidget()
        self.tabs.addTab(self._build_tab_1115(), "Exercise 11.15 (Repeated Complete)")
        self.tabs.addTab(self._build_tab_1118(), "Exercise 11.18 (Same Resource)")
        self.tabs.currentChanged.connect(self._sync_explorer_btn)
        root.addWidget(self.tabs, 1)

        self._clear_view()

    def _build_tab_1115(self) -> QWidget:
        tab = QWidget()
        layout = QVBoxLayout(tab)
        rule = QLabel(
            "<b>Exercise 11.15:</b> Kasus dengan aktivitas <code>W_Assess Potential Fraud</code> "
            "berstatus <code>complete</code> minimal 2 kali.<br>"
            f"<b>Aturan:</b> {RULE_1115}"
        )
        rule.setWordWrap(True)
        layout.addWidget(rule)

        cards = QHBoxLayout()
        self.card_1115_n = MetricCard("Case lolos (unique)")
        self.card_1115_d = MetricCard("Seluruh case")
        self.card_1115_p = MetricCard("Persentase")
        self.card_1115_ev = MetricCard("Event complete (target)")
        for c in (self.card_1115_n, self.card_1115_d, self.card_1115_p, self.card_1115_ev):
            cards.addWidget(c)
        layout.addLayout(cards)

        filt = QHBoxLayout()
        filt.addWidget(QLabel("Filter minimal complete:"))
        self.min_complete_spin = QSpinBox()
        self.min_complete_spin.setRange(2, 999)
        self.min_complete_spin.setValue(2)
        self.min_complete_spin.valueChanged.connect(self._apply_filter_1115)
        filt.addWidget(self.min_complete_spin)
        filt.addStretch(1)
        layout.addLayout(filt)

        self.table_1115 = SearchableTable("Cari case ID (11.15)...")
        self.table_1115.row_activated.connect(lambda cid: self._open_case(self.result_1115, cid))
        layout.addWidget(self.table_1115, 1)
        return tab

    def _build_tab_1118(self) -> QWidget:
        tab = QWidget()
        layout = QVBoxLayout(tab)
        rule = QLabel(
            "<b>Exercise 11.18:</b> Kasus dengan aktivitas <code>W_Assess Potential Fraud</code> "
            "berstatus <code>complete</code> minimal 2 kali oleh <code>org:resource</code> yang sama "
            "dan teridentifikasi (bukan kosong/null).<br>"
            f"<b>Aturan:</b> {RULE_1118}"
        )
        rule.setWordWrap(True)
        layout.addWidget(rule)

        cards = QHBoxLayout()
        self.card_1118_n = MetricCard("Case lolos (unique)")
        self.card_1118_p = MetricCard("Persentase")
        self.card_1118_excl = MetricCard("Gugur (res. beda/kosong)")
        self.card_1118_null = MetricCard("Complete res. kosong")
        for c in (self.card_1118_n, self.card_1118_p, self.card_1118_excl, self.card_1118_null):
            cards.addWidget(c)
        layout.addLayout(cards)

        filt = QHBoxLayout()
        filt.addWidget(QLabel("Filter Resource ID:"))
        self.resource_filter = QLineEdit()
        self.resource_filter.setPlaceholderText("Contoh: User_4 (kosongkan untuk semua)...")
        self.resource_filter.setClearButtonEnabled(True)
        self.resource_filter.textChanged.connect(self._apply_filter_1118)
        filt.addWidget(self.resource_filter, 1)
        layout.addLayout(filt)

        self.table_1118 = SearchableTable("Cari case ID (11.18)...")
        self.table_1118.row_activated.connect(lambda cid: self._open_case(self.result_1118, cid))
        layout.addWidget(self.table_1118, 1)
        return tab

    def _clear_view(self) -> None:
        for c in (
            self.card_1115_n, self.card_1115_d, self.card_1115_p, self.card_1115_ev,
            self.card_1118_n, self.card_1118_p, self.card_1118_excl, self.card_1118_null,
        ):
            c.set_value("-")
        self.lifecycle_banner.setText("Tekan 'Jalankan analisis 11.15 & 11.18' setelah mengimpor log.")
        self._df_1115 = pd.DataFrame(columns=COLS_1115)
        self._df_1118 = pd.DataFrame(columns=COLS_1118)
        self.table_1115.clear()
        self.table_1118.clear()
        self.explorer_btn.setEnabled(False)

    def reset(self) -> None:
        self.result_1115 = None
        self.result_1118 = None
        self.min_complete_spin.setValue(2)
        self.resource_filter.clear()
        self._clear_view()
        self.run_btn.setEnabled(self.log is not None)

    def run(self) -> None:
        if self.log is None:
            QMessageBox.information(self, "Belum ada data", "Impor file XES terlebih dahulu.")
            return
        self.run_btn.setEnabled(False)
        self.lifecycle_banner.setText("Menghitung Exercise 11.15 & 11.18...")
        self.status_message.emit("Menjalankan analisis Exercise 11.15 & 11.18...")
        run_task(_compute, self.log, on_success=self._on_done, on_error=self._on_error)

    def _on_error(self, message: str) -> None:
        self.run_btn.setEnabled(self.log is not None)
        self.lifecycle_banner.setText("Analisis gagal: " + message)

    def _on_done(self, payload) -> None:
        log, res15, res18 = payload
        self.run_btn.setEnabled(self.log is not None)
        if log is not self.log:
            return

        self.result_1115 = res15
        self.result_1118 = res18

        lc = res15["lifecycle_info"]
        counts_str = ", ".join(f"{k}: {fmt_int(v)}" for k, v in lc["lifecycle_counts"].items()) or "tidak ada event target"
        self.lifecycle_banner.setText(
            f"<b>Deteksi Lifecycle XES ({lc['source_attribute']}):</b> {lc['decision']}<br>"
            f"Distribusi pada <code>{lc['target_activity']}</code>: {counts_str}."
        )

        # Populate 11.15
        m15 = res15["metrics"]
        self.card_1115_n.set_value(fmt_int(m15["numerator"]))
        self.card_1115_d.set_value(fmt_int(m15["denominator"]))
        self.card_1115_p.set_value("-" if m15["percentage"] is None else f"{m15['percentage']:.2f}%")
        self.card_1115_ev.set_value(fmt_int(m15["total_complete_events"]))

        rows15 = []
        for cid in res15["case_ids"]:
            ev = res15["evidence"][cid]
            rows15.append({
                COLS_1115[0]: cid,
                COLS_1115[1]: ev["complete_count"],
                COLS_1115[2]: ev["first_complete_timestamp"],
                COLS_1115[3]: ev["last_complete_timestamp"],
                COLS_1115[4]: ", ".join(map(str, ev["positions"])),
                COLS_1115[5]: ", ".join(ev["resources"]),
            })
        self._df_1115 = pd.DataFrame(rows15, columns=COLS_1115)
        self._apply_filter_1115()

        # Populate 11.18
        m18 = res18["metrics"]
        self.card_1118_n.set_value(fmt_int(m18["numerator"]))
        self.card_1118_p.set_value("-" if m18["percentage"] is None else f"{m18['percentage']:.2f}%")
        self.card_1118_excl.set_value(fmt_int(m18["cases_excluded_diff_or_null_resource"]))
        self.card_1118_null.set_value(fmt_int(m18["total_complete_with_null_resource"]))

        rows18 = []
        for cid in res18["case_ids"]:
            ev = res18["evidence"][cid]
            rows18.append({
                COLS_1118[0]: cid,
                COLS_1118[1]: ev["primary_resource"],
                COLS_1118[2]: ev["max_complete_by_same_resource"],
                COLS_1118[3]: ev["resource_summary"],
                COLS_1118[4]: ", ".join(map(str, ev["positions"])),
                COLS_1118[5]: "; ".join(format_value(t) for t in ev["timestamps"]),
            })
        self._df_1118 = pd.DataFrame(rows18, columns=COLS_1118)
        self._apply_filter_1118()

        self._sync_explorer_btn()
        self.result_ready.emit(res15)
        self.result_ready.emit(res18)
        self.status_message.emit(
            f"Exercise 11.15 ({m15['numerator']} case) & 11.18 ({m18['numerator']} case) selesai."
        )

    def _apply_filter_1115(self) -> None:
        if self._df_1115.empty:
            self.table_1115.set_dataframe(self._df_1115)
            return
        min_val = self.min_complete_spin.value()
        filtered = self._df_1115[self._df_1115[COLS_1115[1]] >= min_val]
        self.table_1115.set_dataframe(filtered)

    def _apply_filter_1118(self) -> None:
        if self._df_1118.empty:
            self.table_1118.set_dataframe(self._df_1118)
            return
        query = self.resource_filter.text().strip().lower()
        if not query:
            self.table_1118.set_dataframe(self._df_1118)
            return
        mask = self._df_1118[COLS_1118[3]].astype(str).str.lower().str.contains(query, regex=False)
        self.table_1118.set_dataframe(self._df_1118[mask])

    def _active_result_and_table(self):
        if self.tabs.currentIndex() == 0:
            return self.result_1115, self.table_1115
        return self.result_1118, self.table_1118

    def _sync_explorer_btn(self) -> None:
        res, _ = self._active_result_and_table()
        self.explorer_btn.setEnabled(res is not None)

    def _open_explorer(self) -> None:
        res, table = self._active_result_and_table()
        if res is not None:
            self.show_in_explorer.emit(res, table.current_value())

    def _open_case(self, result: dict | None, case_id: str) -> None:
        if result is not None:
            self.show_in_explorer.emit(result, case_id)

