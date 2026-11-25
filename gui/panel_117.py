"""F03 (sisi GUI) - Exercise 11.7 A-E: Analisis Kasus & Cycle Time (Milik Lintang)."""
from __future__ import annotations

from typing import Optional

import pandas as pd
from PySide6.QtWidgets import (
    QHBoxLayout, QLabel, QMessageBox, QPushButton, QTabWidget, QVBoxLayout, QWidget,
)

from core.exercise_117 import (
    RULE_117_A,
    RULE_117_B,
    RULE_117_C,
    RULE_117_D,
    RULE_117_E,
    exercise_117_all,
)
from gui.panel_base import AnalysisPanelBase
from gui.widgets import MetricCard, SearchableTable, fmt_int
from gui.workers import run_task

COLS_A = ["case_id", "Jumlah Event", "Durasi Trace (Hari)"]
COLS_B = ["case_id", "Jumlah Event", "Durasi Trace (Hari)"]
COLS_C = ["case_id", "Jumlah O_Accepted", "Posisi Event", "Durasi Trace (Hari)"]
COLS_D = ["case_id", "Jumlah O_Refused", "Posisi Event", "Durasi Trace (Hari)"]
COLS_E = ["case_id", "Posisi Terakhir", "Aktivitas Terakhir", "Durasi Trace (Hari)"]


def _compute(log):
    return log, exercise_117_all(log.df)


def _fmt_days(val: Optional[float]) -> str:
    if val is None:
        return "N/A"
    return f"{val:.4f} hari"


class Panel117(AnalysisPanelBase):
    """Panel GUI untuk seluruh Exercise 11.7 (A, B, C, D, E)."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.results: dict[str, dict] = {}

        root = QVBoxLayout(self)
        root.addWidget(QLabel("<h2>Exercise 11.7 - Analisis Kasus &amp; Cycle Time (A-E)</h2>"))

        buttons = QHBoxLayout()
        self.run_btn = QPushButton("Jalankan analisis 11.7 A-E")
        self.reset_btn = QPushButton("Reset hasil")
        self.explorer_btn = QPushButton("Buka di Case Explorer")
        self.run_btn.clicked.connect(self.run)
        self.reset_btn.clicked.connect(self.reset)
        self.explorer_btn.clicked.connect(self._open_explorer)
        for b in (self.run_btn, self.reset_btn, self.explorer_btn):
            buttons.addWidget(b)
        buttons.addStretch(1)
        root.addLayout(buttons)

        # Kartu Ringkasan Atas
        top_cards = QHBoxLayout()
        self.card_top_a = MetricCard("11.7 A (Total Cases)")
        self.card_top_b = MetricCard("11.7 B (Mean Cycle Time)")
        self.card_top_c = MetricCard("11.7 C (Accepted Cases)")
        self.card_top_d = MetricCard("11.7 D (Refused Cases)")
        self.card_top_e = MetricCard("11.7 E (Canceled Cases)")
        for c in (self.card_top_a, self.card_top_b, self.card_top_c, self.card_top_d, self.card_top_e):
            top_cards.addWidget(c)
        root.addLayout(top_cards)

        # Tab Rincian per Sub-soal
        self.tabs = QTabWidget()
        self.tabs.addTab(self._build_tab_a(), "11.7 A (Total Cases)")
        self.tabs.addTab(self._build_tab_b(), "11.7 B (Mean Cycle Time)")
        self.tabs.addTab(self._build_tab_c(), "11.7 C (O_Accepted)")
        self.tabs.addTab(self._build_tab_d(), "11.7 D (O_Refused)")
        self.tabs.addTab(self._build_tab_e(), "11.7 E (O_Cancelled Endpoint)")
        self.tabs.currentChanged.connect(self._sync_explorer_btn)
        root.addWidget(self.tabs, 1)

        self._clear_view()

    def _build_tab_a(self) -> QWidget:
        tab = QWidget()
        layout = QVBoxLayout(tab)
        rule = QLabel(
            "<b>Soal 11.7 A:</b> Hitung jumlah keseluruhan unique case dalam log aktif.<br>"
            f"<b>Aturan:</b> {RULE_117_A}"
        )
        rule.setWordWrap(True)
        layout.addWidget(rule)

        cards = QHBoxLayout()
        self.card_a_n = MetricCard("Total Unique Cases")
        self.card_a_mean = MetricCard("Mean Cycle Time (Hari)")
        for c in (self.card_a_n, self.card_a_mean):
            cards.addWidget(c)
        cards.addStretch(1)
        layout.addLayout(cards)

        self.table_a = SearchableTable("Cari case ID (11.7 A)...")
        self.table_a.row_activated.connect(lambda cid: self._open_case("11.7 A", cid))
        layout.addWidget(self.table_a, 1)
        return tab

    def _build_tab_b(self) -> QWidget:
        tab = QWidget()
        layout = QVBoxLayout(tab)
        rule = QLabel(
            "<b>Soal 11.7 B:</b> Hitung rata-rata cycle time seluruh case (dalam hari) "
            "berdasarkan max(timestamp) - min(timestamp) trace lengkap.<br>"
            f"<b>Aturan:</b> {RULE_117_B}"
        )
        rule.setWordWrap(True)
        layout.addWidget(rule)

        cards = QHBoxLayout()
        self.card_b_mean = MetricCard("Rata-rata Cycle Time")
        self.card_b_denom = MetricCard("Denominator (Total Case)")
        for c in (self.card_b_mean, self.card_b_denom):
            cards.addWidget(c)
        cards.addStretch(1)
        layout.addLayout(cards)

        self.table_b = SearchableTable("Cari case ID (11.7 B)...")
        self.table_b.row_activated.connect(lambda cid: self._open_case("11.7 B", cid))
        layout.addWidget(self.table_b, 1)
        return tab

    def _build_tab_c(self) -> QWidget:
        tab = QWidget()
        layout = QVBoxLayout(tab)
        rule = QLabel(
            "<b>Soal 11.7 C:</b> Hitung jumlah successful cases (mengandung minimal satu <code>O_Accepted</code>) "
            "dan rata-rata cycle time trace lengkapnya.<br>"
            f"<b>Aturan:</b> {RULE_117_C}"
        )
        rule.setWordWrap(True)
        layout.addWidget(rule)

        cards = QHBoxLayout()
        self.card_c_n = MetricCard("Case Lolos (>=1 O_Accepted)")
        self.card_c_d = MetricCard("Denominator Seluruh Case")
        self.card_c_p = MetricCard("Persentase")
        self.card_c_mean = MetricCard("Mean Cycle Time (Full Trace)")
        for c in (self.card_c_n, self.card_c_d, self.card_c_p, self.card_c_mean):
            cards.addWidget(c)
        layout.addLayout(cards)

        self.table_c = SearchableTable("Cari case ID (11.7 C)...")
        self.table_c.row_activated.connect(lambda cid: self._open_case("11.7 C", cid))
        layout.addWidget(self.table_c, 1)
        return tab

    def _build_tab_d(self) -> QWidget:
        tab = QWidget()
        layout = QVBoxLayout(tab)
        rule = QLabel(
            "<b>Soal 11.7 D:</b> Hitung jumlah unsuccessful cases (mengandung minimal satu <code>O_Refused</code>) "
            "dan rata-rata cycle time trace lengkapnya.<br>"
            f"<b>Aturan:</b> {RULE_117_D}"
        )
        rule.setWordWrap(True)
        layout.addWidget(rule)

        cards = QHBoxLayout()
        self.card_d_n = MetricCard("Case Lolos (>=1 O_Refused)")
        self.card_d_d = MetricCard("Denominator Seluruh Case")
        self.card_d_p = MetricCard("Persentase")
        self.card_d_mean = MetricCard("Mean Cycle Time (Full Trace)")
        for c in (self.card_d_n, self.card_d_d, self.card_d_p, self.card_d_mean):
            cards.addWidget(c)
        layout.addLayout(cards)

        self.table_d = SearchableTable("Cari case ID (11.7 D)...")
        self.table_d.row_activated.connect(lambda cid: self._open_case("11.7 D", cid))
        layout.addWidget(self.table_d, 1)
        return tab

    def _build_tab_e(self) -> QWidget:
        tab = QWidget()
        layout = QVBoxLayout(tab)
        rule = QLabel(
            "<b>Soal 11.7 E:</b> Hitung jumlah canceled cases (event paling akhir pada urutan trace adalah <code>O_Cancelled</code>) "
            "dan rata-rata cycle time trace lengkapnya.<br>"
            f"<b>Aturan:</b> {RULE_117_E}"
        )
        rule.setWordWrap(True)
        layout.addWidget(rule)

        cards = QHBoxLayout()
        self.card_e_n = MetricCard("Case Lolos (Endpoint O_Cancelled)")
        self.card_e_d = MetricCard("Denominator Seluruh Case")
        self.card_e_p = MetricCard("Persentase")
        self.card_e_mean = MetricCard("Mean Cycle Time (Full Trace)")
        for c in (self.card_e_n, self.card_e_d, self.card_e_p, self.card_e_mean):
            cards.addWidget(c)
        layout.addLayout(cards)

        self.table_e = SearchableTable("Cari case ID (11.7 E)...")
        self.table_e.row_activated.connect(lambda cid: self._open_case("11.7 E", cid))
        layout.addWidget(self.table_e, 1)
        return tab

    def _clear_view(self) -> None:
        for c in (
            self.card_top_a, self.card_top_b, self.card_top_c, self.card_top_d, self.card_top_e,
            self.card_a_n, self.card_a_mean, self.card_b_mean, self.card_b_denom,
            self.card_c_n, self.card_c_d, self.card_c_p, self.card_c_mean,
            self.card_d_n, self.card_d_d, self.card_d_p, self.card_d_mean,
            self.card_e_n, self.card_e_d, self.card_e_p, self.card_e_mean,
        ):
            c.set_value("-")
        self.table_a.clear()
        self.table_b.clear()
        self.table_c.clear()
        self.table_d.clear()
        self.table_e.clear()
        self.explorer_btn.setEnabled(False)

    def reset(self) -> None:
        self.results = {}
        self._clear_view()
        self.run_btn.setEnabled(self.log is not None)

    def run(self) -> None:
        if self.log is None:
            QMessageBox.information(self, "Belum ada data", "Impor file XES terlebih dahulu.")
            return
        self.run_btn.setEnabled(False)
        self.status_message.emit("Menjalankan analisis Exercise 11.7 A-E...")
        run_task(_compute, self.log, on_success=self._on_done, on_error=self._on_error)

    def _on_error(self, message: str) -> None:
        self.run_btn.setEnabled(self.log is not None)
        self.status_message.emit(f"Analisis 11.7 gagal: {message}")
        QMessageBox.critical(self, "Gagal Menghitung", message)

    def _on_done(self, payload) -> None:
        log, results = payload
        self.run_btn.setEnabled(self.log is not None)
        if log is not self.log:
            return

        self.results = results
        res_a = results["11.7 A"]
        res_b = results["11.7 B"]
        res_c = results["11.7 C"]
        res_d = results["11.7 D"]
        res_e = results["11.7 E"]

        # Kartu Ringkasan Atas
        self.card_top_a.set_value(fmt_int(res_a["case_count"]))
        self.card_top_b.set_value(_fmt_days(res_b["metrics"]["mean_cycle_days"]))
        self.card_top_c.set_value(f"{fmt_int(res_c['case_count'])} ({_fmt_days(res_c['metrics']['mean_cycle_days'])})")
        self.card_top_d.set_value(f"{fmt_int(res_d['case_count'])} ({_fmt_days(res_d['metrics']['mean_cycle_days'])})")
        self.card_top_e.set_value(f"{fmt_int(res_e['case_count'])} ({_fmt_days(res_e['metrics']['mean_cycle_days'])})")

        # Tab A
        self.card_a_n.set_value(fmt_int(res_a["case_count"]))
        self.card_a_mean.set_value(_fmt_days(res_a["metrics"]["mean_cycle_days"]))
        rows_a = [
            {
                COLS_A[0]: cid,
                COLS_A[1]: res_a["evidence"][cid]["events_count"],
                COLS_A[2]: f"{res_a['evidence'][cid]['duration_days']:.4f}",
            }
            for cid in res_a["case_ids"]
        ]
        self.table_a.set_dataframe(pd.DataFrame(rows_a, columns=COLS_A))

        # Tab B
        self.card_b_mean.set_value(_fmt_days(res_b["metrics"]["mean_cycle_days"]))
        self.card_b_denom.set_value(fmt_int(res_b["metrics"]["denominator"]))
        rows_b = [
            {
                COLS_B[0]: cid,
                COLS_B[1]: res_b["evidence"][cid]["events_count"],
                COLS_B[2]: f"{res_b['evidence'][cid]['duration_days']:.4f}",
            }
            for cid in res_b["case_ids"]
        ]
        self.table_b.set_dataframe(pd.DataFrame(rows_b, columns=COLS_B))

        # Tab C
        m_c = res_c["metrics"]
        self.card_c_n.set_value(fmt_int(res_c["case_count"]))
        self.card_c_d.set_value(fmt_int(m_c["denominator"]))
        self.card_c_p.set_value("-" if m_c["percentage"] is None else f"{m_c['percentage']:.2f}%")
        self.card_c_mean.set_value(_fmt_days(m_c["mean_cycle_days"]))
        rows_c = [
            {
                COLS_C[0]: cid,
                COLS_C[1]: res_c["evidence"][cid]["accepted_count"],
                COLS_C[2]: ", ".join(map(str, res_c["evidence"][cid]["highlight_positions"])),
                COLS_C[3]: f"{res_c['evidence'][cid]['duration_days']:.4f}",
            }
            for cid in res_c["case_ids"]
        ]
        self.table_c.set_dataframe(pd.DataFrame(rows_c, columns=COLS_C))

        # Tab D
        m_d = res_d["metrics"]
        self.card_d_n.set_value(fmt_int(res_d["case_count"]))
        self.card_d_d.set_value(fmt_int(m_d["denominator"]))
        self.card_d_p.set_value("-" if m_d["percentage"] is None else f"{m_d['percentage']:.2f}%")
        self.card_d_mean.set_value(_fmt_days(m_d["mean_cycle_days"]))
        rows_d = [
            {
                COLS_D[0]: cid,
                COLS_D[1]: res_d["evidence"][cid]["refused_count"],
                COLS_D[2]: ", ".join(map(str, res_d["evidence"][cid]["highlight_positions"])),
                COLS_D[3]: f"{res_d['evidence'][cid]['duration_days']:.4f}",
            }
            for cid in res_d["case_ids"]
        ]
        self.table_d.set_dataframe(pd.DataFrame(rows_d, columns=COLS_D))

        # Tab E
        m_e = res_e["metrics"]
        self.card_e_n.set_value(fmt_int(res_e["case_count"]))
        self.card_e_d.set_value(fmt_int(m_e["denominator"]))
        self.card_e_p.set_value("-" if m_e["percentage"] is None else f"{m_e['percentage']:.2f}%")
        self.card_e_mean.set_value(_fmt_days(m_e["mean_cycle_days"]))
        rows_e = [
            {
                COLS_E[0]: cid,
                COLS_E[1]: res_e["evidence"][cid]["last_position"],
                COLS_E[2]: res_e["evidence"][cid]["last_activity"],
                COLS_E[3]: f"{res_e['evidence'][cid]['duration_days']:.4f}",
            }
            for cid in res_e["case_ids"]
        ]
        self.table_e.set_dataframe(pd.DataFrame(rows_e, columns=COLS_E))

        self._sync_explorer_btn()

        # Emit 5 hasil terpisah sesuai kontrak
        self.result_ready.emit(res_a)
        self.result_ready.emit(res_b)
        self.result_ready.emit(res_c)
        self.result_ready.emit(res_d)
        self.result_ready.emit(res_e)

        self.status_message.emit("Exercise 11.7 A-E selesai dihitung.")

    def _active_key_and_table(self):
        idx = self.tabs.currentIndex()
        mapping = [
            ("11.7 A", self.table_a),
            ("11.7 B", self.table_b),
            ("11.7 C", self.table_c),
            ("11.7 D", self.table_d),
            ("11.7 E", self.table_e),
        ]
        if 0 <= idx < len(mapping):
            return mapping[idx]
        return "11.7 A", self.table_a

    def _sync_explorer_btn(self) -> None:
        key, _ = self._active_key_and_table()
        self.explorer_btn.setEnabled(key in self.results and self.results[key]["case_count"] > 0)

    def _open_explorer(self) -> None:
        key, table = self._active_key_and_table()
        if key in self.results:
            self.show_in_explorer.emit(self.results[key], table.current_value())

    def _open_case(self, key: str, case_id: str) -> None:
        if key in self.results and case_id:
            self.show_in_explorer.emit(self.results[key], case_id)
