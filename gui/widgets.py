"""Komponen GUI yang dipakai ulang: model tabel DataFrame, tabel berfitur cari, kartu metrik."""
from __future__ import annotations

import numpy as np
import pandas as pd
from PySide6.QtCore import QAbstractTableModel, QModelIndex, QSortFilterProxyModel, Qt, Signal
from PySide6.QtGui import QBrush, QColor
from PySide6.QtWidgets import (
    QAbstractItemView, QFrame, QHeaderView, QLabel, QLineEdit, QTableView, QVBoxLayout, QWidget,
)

DISPLAY = Qt.ItemDataRole.DisplayRole
SORT = Qt.ItemDataRole.UserRole


def fmt_int(n) -> str:
    """Pemisah ribuan gaya Indonesia: 1.234.567"""
    return f"{int(n):,}".replace(",", ".")


def _is_missing(v) -> bool:
    try:
        return bool(pd.isna(v))
    except (TypeError, ValueError):
        return False


def format_value(v) -> str:
    if _is_missing(v):
        return ""
    if isinstance(v, pd.Timestamp):
        return v.strftime("%Y-%m-%d %H:%M:%S")
    if isinstance(v, (bool, np.bool_)):
        return str(v)
    if isinstance(v, (int, np.integer)):
        return str(int(v))
    if isinstance(v, (float, np.floating)):
        return f"{float(v):.4f}"
    return str(v)


def sort_value(v):
    if _is_missing(v):
        return ""
    if isinstance(v, pd.Timestamp):
        return v.isoformat()
    if isinstance(v, (bool, np.bool_)):
        return str(v)
    if isinstance(v, (int, np.integer)):
        return int(v)
    if isinstance(v, (float, np.floating)):
        return float(v)
    return str(v)


class PandasModel(QAbstractTableModel):
    """Model read-only untuk DataFrame; mendukung penyorotan baris."""

    def __init__(self, df: pd.DataFrame | None = None, parent=None):
        super().__init__(parent)
        self._df = df if df is not None else pd.DataFrame()
        self.highlight_rows: set = set()

    def set_dataframe(self, df: pd.DataFrame) -> None:
        self.beginResetModel()
        self._df = df.reset_index(drop=True)
        self.endResetModel()

    def rowCount(self, parent=QModelIndex()):
        return 0 if parent.isValid() else len(self._df)

    def columnCount(self, parent=QModelIndex()):
        return 0 if parent.isValid() else self._df.shape[1]

    def data(self, index, role=DISPLAY):
        if not index.isValid():
            return None
        value = self._df.iat[index.row(), index.column()]
        if role == DISPLAY:
            return format_value(value)
        if role == SORT:
            return sort_value(value)
        if role == Qt.ItemDataRole.BackgroundRole and index.row() in self.highlight_rows:
            return QBrush(QColor("#fff3b0"))
        if role == Qt.ItemDataRole.ForegroundRole and index.row() in self.highlight_rows:
            return QBrush(QColor("#000000"))
        if role == Qt.ItemDataRole.TextAlignmentRole and isinstance(value, (int, float, np.number)):
            return Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
        return None

    def headerData(self, section, orientation, role=DISPLAY):
        if role != DISPLAY:
            return None
        if orientation == Qt.Orientation.Horizontal:
            return str(self._df.columns[section])
        return str(section + 1)


class SearchableTable(QWidget):
    """Tabel dengan kolom pencarian (pada kolom pertama) dan pengurutan."""

    row_selected = Signal(str)   # nilai kolom pertama pada baris yang dipilih
    row_activated = Signal(str)  # nilai kolom pertama pada baris yang di-double-click

    def __init__(self, placeholder: str = "Cari...", parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.search = QLineEdit()
        self.search.setPlaceholderText(placeholder)
        self.search.setClearButtonEnabled(True)
        self.count_label = QLabel("0 baris")

        self.model = PandasModel()
        self.proxy = QSortFilterProxyModel(self)
        self.proxy.setSourceModel(self.model)
        self.proxy.setSortRole(SORT)
        self.proxy.setFilterKeyColumn(0)
        self.proxy.setFilterCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)

        self.view = QTableView()
        self.view.setModel(self.proxy)
        self.view.setSortingEnabled(True)
        self.view.setAlternatingRowColors(True)
        self.view.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.view.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.view.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        header = self.view.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        header.setStretchLastSection(True)

        layout.addWidget(self.search)
        layout.addWidget(self.view, 1)
        layout.addWidget(self.count_label)

        self.search.textChanged.connect(self._on_search)
        self.view.doubleClicked.connect(self._on_double_click)
        self.view.selectionModel().currentRowChanged.connect(self._on_current_changed)

    def set_dataframe(self, df: pd.DataFrame) -> None:
        self.search.blockSignals(True)
        self.search.clear()
        self.search.blockSignals(False)
        self.proxy.setFilterFixedString("")
        self.model.set_dataframe(df)
        self._update_count()

    def clear(self) -> None:
        self.set_dataframe(pd.DataFrame())

    def current_value(self) -> str:
        idx = self.view.currentIndex()
        return self.proxy.index(idx.row(), 0).data() if idx.isValid() else ""

    def select_value(self, value: str) -> bool:
        self.search.clear()
        if self.proxy.rowCount() == 0:
            return False
        hits = self.proxy.match(self.proxy.index(0, 0), DISPLAY, str(value), 1, Qt.MatchFlag.MatchExactly)
        if not hits:
            return False
        self.view.setCurrentIndex(hits[0])
        self.view.scrollTo(hits[0])
        return True

    def _update_count(self) -> None:
        shown, total = self.proxy.rowCount(), self.model.rowCount()
        text = f"{fmt_int(total)} baris" if shown == total else f"{fmt_int(shown)} dari {fmt_int(total)} baris"
        self.count_label.setText(text)

    def _on_search(self, text: str) -> None:
        self.proxy.setFilterFixedString(text)
        self._update_count()

    def _on_double_click(self, index) -> None:
        if index.isValid():
            self.row_activated.emit(str(self.proxy.index(index.row(), 0).data()))

    def _on_current_changed(self, current, _previous) -> None:
        if current.isValid():
            self.row_selected.emit(str(self.proxy.index(current.row(), 0).data()))


class MetricCard(QFrame):
    def __init__(self, title: str, parent=None):
        super().__init__(parent)
        self.setObjectName("metricCard")
        self.setStyleSheet("#metricCard{border:1px solid palette(mid);border-radius:6px;}")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 6, 10, 6)
        self.title = QLabel(title)
        self.value = QLabel("-")
        font = self.value.font()
        font.setPointSize(font.pointSize() + 4)
        font.setBold(True)
        self.value.setFont(font)
        layout.addWidget(self.title)
        layout.addWidget(self.value)

    def set_value(self, text: str) -> None:
        self.value.setText(text)
