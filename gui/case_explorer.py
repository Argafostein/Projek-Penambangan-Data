"""F07 (sisi GUI) - Case Explorer: daftar case dari tiap analisis + rincian urutan event."""
from __future__ import annotations

import pandas as pd
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QAbstractItemView, QComboBox, QHBoxLayout, QHeaderView, QLabel, QSplitter, QTableView, QVBoxLayout, QWidget,
)

from gui.widgets import PandasModel, SearchableTable, fmt_int


def _positions_from(evidence) -> set:
    """Kumpulkan 'highlight_positions' dari bukti (dict atau list dict)."""
    if isinstance(evidence, dict):
        return {int(p) for p in evidence.get("highlight_positions", [])}
    if isinstance(evidence, (list, tuple)):
        found: set = set()
        for item in evidence:
            found |= _positions_from(item)
        return found
    return set()


class CaseExplorer(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.log = None
        self.results: dict = {}

        root = QVBoxLayout(self)
        root.addWidget(QLabel("<h2>Case Explorer</h2>"))

        top = QHBoxLayout()
        top.addWidget(QLabel("Sumber daftar case:"))
        self.source_combo = QComboBox()
        self.source_combo.currentIndexChanged.connect(self._load_source)
        top.addWidget(self.source_combo, 1)
        root.addLayout(top)

        self.info_label = QLabel("Belum ada log aktif.")
        self.info_label.setWordWrap(True)
        root.addWidget(self.info_label)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        self.case_table = SearchableTable("Cari case ID...")
        self.case_table.row_selected.connect(self._show_case)
        splitter.addWidget(self.case_table)

        right = QWidget()
        rl = QVBoxLayout(right)
        rl.setContentsMargins(0, 0, 0, 0)
        self.case_header = QLabel("Pilih case pada daftar di sebelah kiri.")
        self.case_header.setWordWrap(True)
        self.trace_model = PandasModel()
        self.trace_view = QTableView()
        self.trace_view.setModel(self.trace_model)
        self.trace_view.setAlternatingRowColors(True)
        self.trace_view.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.trace_view.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self.trace_view.horizontalHeader().setStretchLastSection(True)
        rl.addWidget(self.case_header)
        rl.addWidget(self.trace_view, 1)
        splitter.addWidget(right)
        splitter.setStretchFactor(0, 2)
        splitter.setStretchFactor(1, 3)
        root.addWidget(splitter, 1)
        self._repopulate(None)

    # ---- API untuk MainWindow ----
    def set_log(self, log) -> None:
        self.log = log
        self.results = {}
        self._repopulate(None)

    def set_results(self, results: dict) -> None:
        keep = self.source_combo.currentData()
        self.results = dict(results)
        self._repopulate(keep if keep in self.results else None)

    def show_result(self, result: dict, case_id: str = "") -> None:
        key = result.get("exercise") if result else None
        if key is not None:
            self.results[key] = result
        self._repopulate(key)
        if case_id and not self.case_table.select_value(case_id):
            self._show_case(case_id)

    # ---- internal ----
    def _repopulate(self, select_key) -> None:
        self.source_combo.blockSignals(True)
        self.source_combo.clear()
        self.source_combo.addItem("Seluruh log", None)
        for key in sorted(self.results):
            self.source_combo.addItem(f"{key} - {fmt_int(self.results[key]['case_count'])} case", key)
        idx = self.source_combo.findData(select_key) if select_key is not None else 0
        self.source_combo.setCurrentIndex(max(idx, 0))
        self.source_combo.blockSignals(False)
        self._load_source()

    def _current_result(self):
        key = self.source_combo.currentData()
        return self.results.get(key) if key is not None else None

    def _load_source(self, *_args) -> None:
        self.trace_model.highlight_rows = set()
        self.trace_model.set_dataframe(pd.DataFrame())
        self.case_header.setText("Pilih case pada daftar di sebelah kiri.")
        if self.log is None:
            self.case_table.clear()
            self.info_label.setText("Belum ada log aktif.")
            return
        res = self._current_result()
        if res is None:
            df = self.log.case_index
            self.info_label.setText(f"Seluruh log: {fmt_int(len(df))} case.")
        else:
            ev = res.get("evidence") or {}
            reasons = [
                ev[c].get("reason", "") if isinstance(ev.get(c), dict) else ""
                for c in res["case_ids"]
            ]
            df = pd.DataFrame({"case_id": res["case_ids"], "bukti": reasons})
            m = res.get("metrics") or {}
            denom = f" | denominator: {fmt_int(m['denominator'])}" if m.get("denominator") is not None else ""
            self.info_label.setText(
                f"Aturan: {res.get('filter_rule', '-')}\nCase terpilih: {fmt_int(res['case_count'])}{denom}"
            )
        self.case_table.set_dataframe(df)

    def _show_case(self, case_id: str) -> None:
        if self.log is None or not case_id:
            return
        trace = self.log.case_trace(case_id)
        if trace.empty:
            self.case_header.setText(f"Case {case_id} tidak ditemukan pada log aktif.")
            return
        res = self._current_result()
        positions = _positions_from((res or {}).get("evidence", {}).get(case_id)) if res else set()
        self.trace_model.highlight_rows = {i for i, p in enumerate(trace["position"]) if int(p) in positions}
        self.trace_model.set_dataframe(trace)
        text = f"<b>Case {case_id}</b> - {fmt_int(len(trace))} event"
        if positions:
            text += " (baris kuning = event bukti)"
        self.case_header.setText(text)
