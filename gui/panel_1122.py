"""F06 (sisi GUI) - Exercise 11.22: O_Cancelled kemudian O_Accepted."""
from __future__ import annotations

import pandas as pd
from PySide6.QtWidgets import QHBoxLayout, QLabel, QMessageBox, QPushButton, QVBoxLayout

from core.exercise_1122 import FILTER_RULE, exercise_1122
from gui.panel_base import AnalysisPanelBase
from gui.widgets import MetricCard, SearchableTable, fmt_int
from gui.workers import run_task

COLS = ["case_id", "O_Cancelled (urutan)", "O_Cancelled (waktu)", "O_Accepted (urutan)", "O_Accepted (waktu)"]


def _compute(log):
    return log, exercise_1122(log.df)


class Panel1122(AnalysisPanelBase):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.result = None
        root = QVBoxLayout(self)
        root.addWidget(QLabel("<h2>Exercise 11.22 - O_Cancelled kemudian O_Accepted</h2>"))
        rule = QLabel(
            "Pertanyaan: adakah O_Cancelled yang kemudian diikuti O_Accepted, dan berapa persentase case-nya?<br>"
            f"<b>Aturan:</b> {FILTER_RULE}"
        )
        rule.setWordWrap(True)
        root.addWidget(rule)

        buttons = QHBoxLayout()
        self.run_btn = QPushButton("Jalankan analisis")
        self.reset_btn = QPushButton("Reset hasil")
        self.explorer_btn = QPushButton("Buka di Case Explorer")
        self.run_btn.clicked.connect(self.run)
        self.reset_btn.clicked.connect(self.reset)
        self.explorer_btn.clicked.connect(self._open_explorer)
        for b in (self.run_btn, self.reset_btn, self.explorer_btn):
            buttons.addWidget(b)
        buttons.addStretch(1)
        root.addLayout(buttons)

        cards = QHBoxLayout()
        self.card_n = MetricCard("Case lolos (pembilang)")
        self.card_d = MetricCard("Seluruh case (denominator)")
        self.card_p = MetricCard("Persentase")
        self.card_both = MetricCard("Case memuat keduanya (info)")
        for c in (self.card_n, self.card_d, self.card_p, self.card_both):
            cards.addWidget(c)
        root.addLayout(cards)

        self.formula = QLabel("")
        self.formula.setWordWrap(True)
        root.addWidget(self.formula)

        self.table = SearchableTable("Cari case ID...")
        self.table.row_activated.connect(self._open_case)
        root.addWidget(self.table, 1)
        self._clear_view()

    def _clear_view(self) -> None:
        for c in (self.card_n, self.card_d, self.card_p, self.card_both):
            c.set_value("-")
        self.formula.setText("Tekan 'Jalankan analisis'.")
        self.table.clear()
        self.explorer_btn.setEnabled(False)

    def reset(self) -> None:
        self.result = None
        self._clear_view()
        self.run_btn.setEnabled(self.log is not None)

    def run(self) -> None:
        if self.log is None:
            QMessageBox.information(self, "Belum ada data", "Impor file XES terlebih dahulu.")
            return
        self.run_btn.setEnabled(False)
        self.formula.setText("Menghitung...")
        self.status_message.emit("Menjalankan analisis Exercise 11.22...")
        run_task(_compute, self.log, on_success=self._on_done, on_error=self._on_error)

    def _on_error(self, message: str) -> None:
        self.run_btn.setEnabled(self.log is not None)
        self.formula.setText("Analisis gagal: " + message)

    def _on_done(self, payload) -> None:
        log, result = payload
        self.run_btn.setEnabled(self.log is not None)
        if log is not self.log:  # hasil dari file lama, abaikan
            return
        self.result = result
        m = result["metrics"]
        self.card_n.set_value(fmt_int(m["numerator"]))
        self.card_d.set_value(fmt_int(m["denominator"]))
        self.card_p.set_value("-" if m["percentage"] is None else f"{m['percentage']:.2f}%")
        self.card_both.set_value(fmt_int(m["cases_with_both_activities"]))
        pct = "-" if m["percentage"] is None else f"{m['percentage']:.4f}%"
        self.formula.setText(
            f"{fmt_int(m['numerator'])} / {fmt_int(m['denominator'])} x 100% = {pct}. "
            "Dihitung per case (satu case dihitung sekali)."
        )
        rows = [
            {
                COLS[0]: cid,
                COLS[1]: ev["cancelled_position"],
                COLS[2]: ev["cancelled_timestamp"],
                COLS[3]: ev["accepted_position"],
                COLS[4]: ev["accepted_timestamp"],
            }
            for cid, ev in ((c, result["evidence"][c]) for c in result["case_ids"])
        ]
        self.table.set_dataframe(pd.DataFrame(rows, columns=COLS))
        self.explorer_btn.setEnabled(True)
        self.result_ready.emit(result)
        self.status_message.emit(f"Exercise 11.22 selesai: {m['numerator']} case.")

    def _open_explorer(self) -> None:
        if self.result is not None:
            self.show_in_explorer.emit(self.result, self.table.current_value())

    def _open_case(self, case_id: str) -> None:
        if self.result is not None:
            self.show_in_explorer.emit(self.result, case_id)
